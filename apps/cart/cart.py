from decimal import Decimal
from django.conf import settings
from apps.catalog.models import ProductVariant
from .models import Cart, CartItem


class SessionCart:
    """
    A unified cart interface that handles both session-based (guest) 
    and database-backed (authenticated user) carts.
    """
    
    def __init__(self, request):
        """Initialize the cart."""
        self.session = request.session
        self.user = request.user
        cart_session = self.session.get(settings.CART_SESSION_ID)
        
        if not cart_session:
            # Save an empty cart in the session
            cart_session = self.session[settings.CART_SESSION_ID] = {}
        
        self.cart_session = cart_session

    def add(self, variant, quantity=1, override_quantity=False):
        """Add a product variant to the cart or update its quantity."""
        variant_id = str(variant.id)
        
        if self.user.is_authenticated:
            # Database cart
            cart, created = Cart.objects.get_or_create(user=self.user)
            item, created = CartItem.objects.get_or_create(cart=cart, variant=variant)
            
            if override_quantity:
                item.quantity = quantity
            else:
                item.quantity += quantity
            item.save()
        else:
            # Session cart
            if variant_id not in self.cart_session:
                self.cart_session[variant_id] = {'quantity': 0}
            
            if override_quantity:
                self.cart_session[variant_id]['quantity'] = quantity
            else:
                self.cart_session[variant_id]['quantity'] += quantity
            
            self.save()

    def remove(self, variant):
        """Remove a product variant from the cart."""
        variant_id = str(variant.id)
        
        if self.user.is_authenticated:
            # Database cart
            CartItem.objects.filter(cart__user=self.user, variant=variant).delete()
        else:
            # Session cart
            if variant_id in self.cart_session:
                del self.cart_session[variant_id]
                self.save()

    def __iter__(self):
        """Iterate over the items in the cart and get the products from the database."""
        variant_ids = self.cart_session.keys()
        
        if self.user.is_authenticated:
            # For authenticated users, we use the database items
            cart, _ = Cart.objects.get_or_create(user=self.user)
            items = cart.items.all().select_related('variant', 'variant__product', 'variant__price')
            
            for item in items:
                yield {
                    'variant': item.variant,
                    'quantity': item.quantity,
                    'total_price': item.total_price,
                    'unit_price': item.unit_price,
                    'item_id': item.id
                }
        else:
            # For guests, we use session items
            variants = ProductVariant.objects.filter(id__in=variant_ids).select_related('product', 'price')
            cart_data = self.cart_session.copy()
            
            for variant in variants:
                item = cart_data[str(variant.id)]
                item['variant'] = variant
                item['unit_price'] = variant.price.effective_price if hasattr(variant, 'price') else Decimal('0')
                item['total_price'] = item['unit_price'] * item['quantity']
                yield item

    def __len__(self):
        """Count all items in the cart."""
        if self.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=self.user)
            return sum(item.quantity for item in cart.items.all())
        return sum(item['quantity'] for item in self.cart_session.values())

    def get_total_price(self):
        """Calculate total cost of items in the cart."""
        if self.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=self.user)
            return sum(item.total_price for item in cart.items.all())
        
        total = Decimal('0')
        variants = ProductVariant.objects.filter(id__in=self.cart_session.keys()).select_related('price')
        prices = {str(v.id): (v.price.effective_price if hasattr(v, 'price') else Decimal('0')) for v in variants}
        
        for variant_id, item in self.cart_session.items():
            total += prices.get(variant_id, Decimal('0')) * item['quantity']
        return total

    def clear(self):
        """Remove cart from session and database."""
        if self.user.is_authenticated:
            CartItem.objects.filter(cart__user=self.user).delete()
        
        if settings.CART_SESSION_ID in self.session:
            del self.session[settings.CART_SESSION_ID]
            self.save()

    def save(self):
        """Mark the session as modified to ensure it gets saved."""
        self.session.modified = True

    def merge_with_user_cart(self):
        """Move session items to the user's database cart."""
        if not self.user.is_authenticated or not self.cart_session:
            return
            
        cart, created = Cart.objects.get_or_create(user=self.user)
        variant_ids = self.cart_session.keys()
        variants = ProductVariant.objects.filter(id__in=variant_ids)
        
        for variant in variants:
            session_qty = self.cart_session[str(variant.id)]['quantity']
            item, created = CartItem.objects.get_or_create(cart=cart, variant=variant)
            
            if created:
                item.quantity = session_qty
            else:
                # If item already exists in DB, we could either override or add. 
                # Adding is usually more user-friendly.
                item.quantity += session_qty
            item.save()
            
        # Clear the session cart after merging
        del self.session[settings.CART_SESSION_ID]
        self.save()
