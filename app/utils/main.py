from datetime import datetime, date, timedelta
from app import db
from app.models.products import Product, Brand, Category


def validate_product_id_type(product_id):
    try:
        product_id = int(product_id)
    except ValueError:
        return None
    return product_id


def is_valid_json_for_model(data, model, return_dict=False) -> ([db.Model, None], [str, None]):
    # We're not strongly require primary keys, possible nullable values and columns with provided defaults
    column_names = [col.name for col in model.__table__.columns if not col.primary_key]
    required_column_names = [col.name for col in model.__table__.columns if
                             not col.nullable and not col.primary_key and not col.default]

    # Easy way to make a fast check on required fields
    if not all(map(data.__contains__, required_column_names)):
        return None, f"Missing required field(s); List of all required fields: {required_column_names}"

    for key in data:  # Checking keys in request
        if key in column_names:  # Searching for key in table
            column = getattr(model, key)  # Getting SQLAlchemy object

            # Checking python type. Unfortunately it will fail on datetime, date and etc. Requires additional conversion
            if isinstance(column.type.python_type, datetime):
                # So, datetime usually provided as integer UTC timestamp, isn't it?
                #
                # There's also a way to parse via `datetime.strptime`
                try:
                    data[key] = datetime.fromtimestamp(data[key])
                except (TypeError, ValueError):
                    return None, f"Key '{key}' with value '{data[key]}' does not have viable conversion to '{column.type.python_type}'"
            # Check date
            if isinstance(column.type.python_type, date):
                try:
                    data[key] = date.fromtimestamp(data[key])
                except (TypeError, ValueError):
                    return None, f"Key '{key}' with value '{data[key]}' does not have viable conversion to '{column.type.python_type}'"

            # There's also an option available for automatic data conversion, not sure if necessary
            # try:
            #   data[key] = column.type.python_type(data[key])
            # except (ValueError, TypeError):
            #   print("At least we tried")

            # Check `NONE` values
            if data[key] is None and not column.nullable:
                return None, f"Key '{key}' must be non-empty"

            # Check other types
            elif isinstance(data[key], column.type.python_type) or (data[key] is None and column.nullable):
                if hasattr(column.type, 'length'):
                    desired_length = column.type.length
                    if len(data[key]) > desired_length:
                        return None, f"Key '{key}' does not match desired length of {desired_length}"

            else:
                return None, f"Key '{key}' with type '{type(data[key])}' does not match desired type '{column.type.python_type}'"

    # All keys tested, now we can safely serialize data
    obj_dict = {}
    for key in column_names:
        if key in data:
            obj_dict[key] = data[key]

    if return_dict:
        return obj_dict, None

    return model(**obj_dict), None


def validate_product_obj(product: Product) -> (bool, [str, db.Model]):
    if not 1 <= len(product.categories) <= 5:
        return None, "Categories count mismatch"
    if product.expiration_date:
        if product.expiration_date < datetime.utcnow() + timedelta(days=30):
            return None, "Product Expired"
    if not product.featured and product.rating > 8:
        product.featured = True

    return product, None


def validate_category(data, new_product: Product):
    if isinstance(data['categories'], list):
        for category in set(data['categories']):
            if not isinstance(category, int):
                return None, f"Category '{category}' must be an integer, not '{type(category)}'"
            weak_category = Category.query.get(category)
            if weak_category:
                # Such category exists
                new_product.categories.append(weak_category)
            else:
                # No category with such ID.
                # To simplify this part of code let's just create a category.

                # This may fail due to VARCHAR(50), let's assume we don't have more than 10^40 categories
                new_category = Category(id=category, name=f'Category {category}')
                new_product.categories.append(new_category)

        return new_product, None
    else:
        return None, "Key 'categories' must be a list"


def validate_brand(data, new_product: Product):
    if 'brand_id' in data:
        brand_id = data['brand_id']
        if not isinstance(brand_id, int):
            return None, f"Brand id '{brand_id}' must be an integer, not '{type(brand_id)}'"

        weak_brand = Brand.query.get(brand_id)
        if weak_brand:
            # Such brand exists
            weak_brand.products.append(new_product)
            new_product.brand_id = brand_id
        else:
            # No brand with such ID.
            # To simplify this part of code let's just create a brand.

            # This may fail due to VARCHAR(50), let's assume we don't have more than 10^40 different Brands
            new_brand = Brand(id=brand_id, name=f'Brand {brand_id}', country_code='US')

            db.session.add(new_brand)
            new_product.brand_id = brand_id

    return new_product, None
