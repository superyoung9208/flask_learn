from watchlist import app,db
from watchlist.models import User,Movie
import click

@app.cli.command()  # 注册为命令
@click.option('--drop', is_flag=True, help='Create after drop.')
def initdb(drop):
    if drop:
        db.drop_all()
    db.create_all()
    click.echo("Initialized database.")  # 输出提示信息


@app.cli.command()
def forge():
    db.create_all()
    name = 'Grey Li'
    movies = [
        {'title': 'My Neighbor Totoro', 'year': '1988'},
        {'title': 'Dead Poets Society', 'year': '1989'},
        {'title': 'A Perfect World', 'year': '1993'},
        {'title': 'Leon', 'year': '1994'},
        {'title': 'Mahjong', 'year': '1996'},
        {'title': 'Swallowtail Butterfly', 'year': '1996'},
        {'title': 'King of Comedy', 'year': '1999'},
        {'title': 'Devils on the Doorstep', 'year': '1999'},
        {'title': 'WALL-E', 'year': '2008'},
    ]
    user = User(name=name)
    for m in movies:
        movie = Movie(title=m['title'], year=m['year'])
        db.session.add(movie)
    db.session.add(user)
    db.session.commit()
    click.echo('Done')


# confirmation_prompt=True 会要求二次确认输入
# hide_input=True 会让密码输入隐藏
@app.cli.command()
@click.option('--username', prompt=True, help="The username used login")
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help="The password used login")
def admin(username, password):
    """create_user"""
    db.create_all()
    user = User.query.first()
    if user is not None:
        click.echo("updating user")
        user.name = username
        user.password = password
    else:
        click.echo("create user")
        user = User()
        user.name = username
        user.password = password
        db.session.add(user)

    db.session.commit()
    click.echo("Done.")