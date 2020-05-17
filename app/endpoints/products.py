from flask import Blueprint, jsonify, request
from sqlalchemy.exc import SQLAlchemyError
from app.models.products import Product, db
from app.utils.main import validate_product_id_type, is_valid_json_for_model, validate_product_obj, validate_brand, \
    validate_category

products_blueprint = Blueprint('products', __name__)


@products_blueprint.route('/products', methods=['GET'])
def get_products():
    return jsonify({
        'result': [p.serialized for p in Product.query.all()]
    })


@products_blueprint.route('/products/<product_id>', methods=['GET'])
def get_product_by_id(product_id):
    product_id = validate_product_id_type(product_id)
    if product_id is None:
        return jsonify({'error': "Wrong product_id parameter type"}), 400
    product = Product.query.get(product_id)
    if product:
        return jsonify({'result': product.serialized})
    else:
        return jsonify({'error': "Product not found"}), 404


@products_blueprint.route('/products', methods=['POST'])
def create_product():
    # get_json() function automatically parses json data or responses with 400 error code on fail
    # Requires application/json mimetype
    data = request.get_json()
    if not data:
        return jsonify({'error': "Empty request"}), 400

    new_product, error = is_valid_json_for_model(data, Product)
    if error:
        return jsonify({'error': error}), 400
    else:

        # Since `is_valid_json_for_model` func does not deal with foreign keys relations,
        # we should implement categories/brands handling manually
        if 'categories' in data:
            new_product, error = validate_category(data, new_product)
            if error:
                return jsonify({'error': error}), 400
        else:
            return jsonify({'error': "Missing categories key"}), 400

        new_product, error = validate_brand(data, new_product)
        if error:
            return jsonify({'error': error}), 400

        new_product, error = validate_product_obj(new_product)
        if error:
            return jsonify({'error': error}), 400

        try:
            db.session.add(new_product)
            db.session.commit()
        except SQLAlchemyError as e:
            # Log Exception
            return jsonify({'error': "Internal database error"}), 500

        try:
            queried_product = Product.query.get(new_product.id)
        except SQLAlchemyError as e:
            # Log Exception
            return jsonify({'error': "Internal database error"}), 500

        return jsonify({'result': queried_product.serialized})


@products_blueprint.route('/products/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    product_id = validate_product_id_type(product_id)
    if product_id is None:
        return jsonify({'error': "Wrong 'product_id' parameter type, must me 'int"}), 400

    product = Product.query.get(product_id)
    if product:
        db.session.delete(product)
        db.session.commit()
        return jsonify({'result': "Product deleted"})
    else:
        return jsonify({'error': "Product not found"}), 404


@products_blueprint.route('/products/<product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.get_json()
    if not data:
        return jsonify({'error': "Empty request"}), 400

    product_id = validate_product_id_type(product_id)
    if product_id is None:
        return jsonify({'error': "Wrong 'product_id' parameter type, must be 'int'"}), 400

    product = Product.query.get(product_id)
    if product:
        json_product = product.serialized

        merged_product = {**json_product, **data}
        if 'brand_id' not in merged_product:
            merged_product['brand_id'] = json_product['brand']['id']
        if 'categories' not in data:
            data['categories'] = []

        updated_product_json, error = is_valid_json_for_model(merged_product, Product, return_dict=True)
        if updated_product_json:
            for key, value in updated_product_json.items():
                setattr(product, key, value)

            updated_product, error = validate_category(data, product)
            if error:
                return jsonify({'error': error}), 400

            updated_product, error = validate_brand(data, updated_product)
            if error:
                return jsonify({'error': error}), 400

            try:
                db.session.commit()
            except SQLAlchemyError as e:
                # Log Exception
                return jsonify({'error': "Internal database error"}), 500

            try:
                queried_product = Product.query.get(updated_product.id)
            except SQLAlchemyError as e:
                # Log Exception
                return jsonify({'error': "Internal database error"}), 500

            return jsonify({'result': queried_product.serialized})
        else:
            return jsonify({'error': error}), 400
    else:
        return jsonify({'error': "Product not found"}), 404
