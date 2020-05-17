from flask import json

init_product = {
    'name': 'Product 1',
    'rating': 9.0,
    'brand_id': 5,
    'items_in_stock': 9,
    'categories': [1, 5, 16]
}


def test_empty_products(client):
    rv = client.get('/products', headers={'mime-type': 'application/json'})
    data = json.loads(rv.get_data(as_text=True))
    assert {'result': []} == data


def test_invalid_categories_type(client):
    rv = client.post('/products', json=
    {
        'name': 'Food Product',
        'rating': 5.0,
        'brand_id': 3,
        'items_in_stock': 12,
        'categories': 'Food'
    })
    data = json.loads(rv.get_data(as_text=True))
    error = data['error']
    assert rv.status_code == 400
    assert error == "Key 'categories' must be a list"


def test_create_product(client):
    rv = client.post('/products', json=init_product)
    data = json.loads(rv.get_data(as_text=True))
    result = data['result']
    assert result['categories'] == [
        {'id': 1, 'name': 'Category 1'},
        {'id': 5, 'name': 'Category 5'},
        {'id': 16, 'name': 'Category 16'}
    ]
    assert result['featured'] == True
    assert result['items_in_stock'] == 9
    assert result['name'] == 'Product 1'
    assert result['brand'] == {'country_code': 'US', 'id': 5, 'name': 'Brand 5'}


def test_get_product(client):
    rv = client.get('/products/1', headers={'mime-type': 'application/json'})
    data = json.loads(rv.get_data(as_text=True))
    result = data['result']
    assert result['categories'] == [
        {'id': 1, 'name': 'Category 1'},
        {'id': 5, 'name': 'Category 5'},
        {'id': 16, 'name': 'Category 16'}
    ]
    assert result['featured'] == True
    assert result['items_in_stock'] == 9
    assert result['name'] == 'Product 1'
    assert result['brand'] == {'country_code': 'US', 'id': 5, 'name': 'Brand 5'}


def test_update_product(client):
    updated_product = {'name': 'Product Edited', 'items_in_stock': 4}
    rv = client.put('/products/1', json=updated_product)
    data = json.loads(rv.get_data(as_text=True))
    result = data['result']
    assert result['name'] == updated_product['name']
    assert result['items_in_stock'] == 4
    assert result['id'] == 1


def test_delete_product(client):
    rv = client.delete('/products/1')
    data = json.loads(rv.get_data(as_text=True))
    result = data['result']
    assert result == 'Product deleted'

    rv = client.get('/products', headers={'mime-type': 'application/json'})
    data = json.loads(rv.get_data(as_text=True))
    assert {'result': []} == data


def test_invalid_product(client):
    rv = client.post('/products', json=
    {
        'name': 'Product 2',
        'brand_id': 7,
        'rating': 4.3,
        'categories': [1, 2, 3, 4, 5, 6, 7],
        'items_in_stock': 999
    })
    data = json.loads(rv.get_data(as_text=True))
    error = data['error']
    assert rv.status_code == 400
    assert error == 'Categories count mismatch'


def test_invalid_types(client):
    rv = client.post('/products', json=
    {
        'name': 'Product 3',
        'brand_id': '7',
        'rating': 4,
        'categories': [{'name': 'Category 1', 'id': 2}],
        'items_in_stock': None
    })
    data = json.loads(rv.get_data(as_text=True))
    error = data['error']
    assert rv.status_code == 400
    assert error == "Key 'brand_id' with type '<class 'str'>' does not match desired type '<class 'int'>'"
