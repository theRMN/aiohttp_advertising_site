from aiohttp import web
from gino import Gino
import datetime

PG_DSN = 'postgresql://admin:admin@127.0.0.1:5432/advertising_site'

routes = web.RouteTableDef()
app = web.Application()
db = Gino()


class Advertising(db.Model):

    __tablename__ = 'app_advertising'

    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(64), index=True, unique=True, nullable=False)
    description = db.Column(db.String(), index=True, unique=True)
    create_at = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
    creator_id = db.Column(db.Integer(), db.ForeignKey('app_creator.id'), nullable=False)


class Creator(db.Model):

    __tablename__ = 'app_creator'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True, nullable=False)


class AdvertisingView(web.View):

    async def get(self):
        id = int(self.request.match_info['id'])
        data = await Advertising.get(id)
        data.create_at = str(data.create_at)
        return web.json_response(data.to_dict())

    async def post(self):
        data = await self.request.json()
        new_obj = await Advertising.create(**data)
        new_obj.create_at = str(new_obj.create_at)
        return web.json_response(new_obj.to_dict())

    async def patch(self):
        data = await self.request.json()
        id = int(self.request.match_info['id'])
        response = await Advertising.update.values(**data).where(Advertising.id == id).gino.status()

        if response[0] == 'UPDATE 1':
            return web.json_response(data)
        else:
            return web.json_response({'http_status': 404})

    async def delete(self):
        id = int(self.request.match_info['id'])
        response = await Advertising.delete.where(Advertising.id == id).gino.status()

        if response[0] == 'DELETE 1':
            return web.json_response({'http_status': 204})
        else:
            return web.json_response({'http_status': 404})


async def orm_context(app):
    await db.set_bind(PG_DSN)
    await db.gino.create_all()
    yield
    await db.pop_bind().close()

app.router.add_routes([web.get('/advertising/{id}', AdvertisingView)])
app.router.add_routes([web.post('/advertising', AdvertisingView)])
app.router.add_routes([web.patch('/advertising/{id}', AdvertisingView)])
app.router.add_routes([web.delete('/advertising/{id}', AdvertisingView)])
app.cleanup_ctx.append(orm_context)

if __name__ == '__main__':
    web.run_app(app)
