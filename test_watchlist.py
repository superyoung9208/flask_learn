"""
File:test_watchlist.py
Author:laoyang
"""

import unittest
from watchlist import app, db
from watchlist.commands import forge, initdb
from watchlist.models import User, Movie


class WatchlistTestCase(unittest.TestCase):
    """应用测试"""

    def setUp(self):
        """更新配置"""
        app.config.update(
            TESTING=True,
            SQLALCHEMY_DATABASE_URI='sqlite:///:memory:'
        )

        db.create_all()
        user = User()
        user.name = "Test"
        user.password = "123"
        movie = Movie()
        movie.title = "Test Movie"
        movie.year = '1900'
        db.session.add_all([user, movie])
        db.session.commit()

        self.client = app.test_client()  # 创建测试客户端
        self.ruuner = app.test_cli_runner()  # 创建测试命令运行器

    def tearDown(self):
        """收尾工作"""
        db.session.remove()
        db.drop_all()

    def test_app_exist(self):
        """测试app是否存在"""
        self.assertIsNotNone(app)

    def test_app_is_testing(self):
        """测试是否是测试模式"""
        self.assertTrue(app.config["TESTING"])

    def test_404_page(self):
        """测试404页面"""
        response = self.client.get("/noting")
        data = response.get_data(as_text=True)
        self.assertIn("Page Not Found - 404", data)
        self.assertIn('Go Back', data)
        self.assertEqual(response.status_code, 404)

    def test_index_page(self):
        """测试首页"""
        response = self.client.get("/")
        data = response.get_data(as_text=True)
        self.assertIn("Test\'s Watchlist", data)
        self.assertNotIn("XXX", data)
        self.assertEqual(response.status_code, 200)

    def login(self):
        """辅助方法,用户登陆"""
        self.client.post("/login", data={
            "username": "Test",
            "password": "123"
        }, follow_redirects=True)

    def test_create_item(self):
        """测试创建条目"""
        self.login()

        # 创建测试条目操作
        response = self.client.post("/", data={
            'title': 'Test Movie',
            'year': '2019'}, follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item created.', data)
        self.assertIn('Test Movie', data)

        # 测试创建条目操作，但电影标题为空
        response = self.client.post('/', data={
            'title': '',
            'year': '1992'
        }, follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item created.', data)
        self.assertIn('Invalid input', data)

        # 测试创建条目操作，但电影年份为空

        response = self.client.post('/', data={
            'title': 'laoyang',
            'year': ''
        }, follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item created.', data)
        self.assertIn('Invalid input', data)

    def test_update_item(self):
        """测试更新条目"""
        response = self.client.get('/movies/1')
        data = response.get_data(as_text=True)
        self.assertIn('Test Movie', data)
        self.assertIn('Edit item', data)
        self.assertEqual(response.status_code, 200)

        # 测试更新一个条目
        response = self.client.post('/movies/1', data={
            'title': 'Test put item',
            'year': '1998'
        }, follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Test put item', data)
        self.assertIn('Item updated.', data)

    def test_remove_item(self):
        """测试删除一个条目"""
        response = self.client.delete('/movies/1', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item deleted.', data)
        self.assertNotIn('Test Movie', data)

    def test_login_protect(self):
        """测试登陆保护"""
        response = self.client.get('/')
        data = response.get_data(as_text=True)
        self.assertNotIn('Logout', data)
        self.assertNotIn('Settings', data)
        self.assertNotIn('Edit', data)
        self.assertNotIn('<form method="post">', data)

    def test_login(self):
        """测试登陆"""
        response = self.client.post('/login', data=dict(username='Test', password='123'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Logout', data)
        self.assertIn('Settings', data)
        self.assertIn('Edit', data)
        self.assertIn('<form method="post">', data)
        self.assertIn("Login success", data)

        # 异常测试,错误密码
        response = self.client.post('/login', data=dict(username='Test', password='1233'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn("Invalid username or password", data)

        # 异常测试,输入空数据
        response = self.client.post('/login', data=dict(username='Test', password=''), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn("Invalid input", data)

    def test_logout(self):
        """测试登出"""
        self.login()

        response = self.client.get('/logout', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn("Good bye", data)
        self.assertNotIn('Logout', data)
        self.assertNotIn('Settings', data)
        self.assertNotIn('Delete', data)
        self.assertNotIn('Edit', data)
        self.assertNotIn('<form method="post">', data)

    def test_settings(self):
        """测试设置页面"""
        self.login()
        response = self.client.get('/settings', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Settings', data)
        self.assertIn('Test', data)

        response = self.client.post('/settings', data=dict(name="laoyang"), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('setting updated', data)
        self.assertIn('laoyang\'s Watchlist', data)

        response = self.client.post('/settings', data=dict(name=""), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Invalid input', data)
        self.assertNotIn('setting updated', data)

    def test_forge_command(self):
        """测试forge命令"""
        result = self.ruuner.invoke(forge)
        self.assertIn('Done', result.output)
        self.assertNotEqual(Movie.query.count(), 0)

    def test_initdb_command(self):
        """测试initdb命令"""
        result = self.ruuner.invoke(initdb)
        self.assertIn('Initialized database.', result.output)

    def test_admin_command(self):
        """测试admin命令"""
        db.drop_all()
        db.create_all()
        result = self.ruuner.invoke(args=['admin', '--username', 'laoyang', '--password', '123'])
        self.assertIn('create user', result.output)
        self.assertIn('Done.', result.output)
        self.assertEqual(User.query.count(), 1)
        self.assertEqual(User.query.first().name, 'laoyang')
        self.assertTrue(User.query.first().check_password('123'))

    def test_admin_command_update(self):
        """测试更新admin命令"""
        result = self.ruuner.invoke(args=['admin', '--username', 'peter', '--password', '456'])
        self.assertIn('updating user', result.output)
        self.assertIn('Done.', result.output)
        self.assertEqual(User.query.count(), 1)
        self.assertEqual(User.query.first().name, 'peter')
        self.assertTrue(User.query.first().check_password('456'))


if __name__ == '__main__':
    unittest.main()
