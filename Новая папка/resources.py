from flask_restful import Resource, reqparse
from models import Item, db

parser = reqparse.RequestParser()
parser.add_argument('name', required=True, help='Name cannot be blank')

class ItemResource(Resource):
    def get(self, item_id):
        item = Item.query.get_or_404(item_id)
        return {'id': item.id, 'name': item.name}

    def delete(self, item_id):
        item = Item.query.get_or_404(item_id)
        db.session.delete(item)
        db.session.commit()
        return '', 204

    def put(self, item_id):
        args = parser.parse_args()
        item = Item.query.get_or_404(item_id)
        item.name = args['name']
        db.session.commit()
        return {'id': item.id, 'name': item.name}

class ItemListResource(Resource):
    def get(self):
        items = Item.query.all()
        return [{'id': item.id, 'name': item.name} for item in items]

    def post(self):
        args = parser.parse_args()
        new_item = Item(name=args['name'])
        db.session.add(new_item)
        db.session.commit()
        return {'id': new_item.id, 'name': new_item.name}, 201