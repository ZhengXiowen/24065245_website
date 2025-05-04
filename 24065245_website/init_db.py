import os
from app import app, db, Book, User, Comment

if os.path.exists('books.db'):
    os.remove('books.db')

with app.app_context():
    db.create_all()

    user = User(username='admin', email='admin@example.com')
    user.set_password('admin')
    db.session.add(user)
    db.session.commit()

    books = [
        Book(
            name_en="The Great Gatsby",
            name_zh="了不起的盖茨比",
            description_en="A classic novel set in the Jazz Age, exploring themes of wealth and the American Dream.",
            description_zh="以爵士时代为背景的经典小说，探讨财富与美国梦等主题。",
            price=10.99,
            env_impact=5,
            image="book1.jpg"
        ),
        Book(
            name_en="1984",
            name_zh="一九八四",
            description_en="George Orwell's dystopian novel about totalitarian surveillance and loss of individuality.",
            description_zh="乔治·奥威尔的反乌托邦小说，讲述极权监视与个人自由丧失。",
            price=8.99,
            env_impact=7,
            image="book2.jpg"
        ),
        Book(
            name_en="Pride and Prejudice",
            name_zh="傲慢与偏见",
            description_en="A romantic novel by Jane Austen criticizing the British landed gentry of the early 19th century.",
            description_zh="简·奥斯汀的浪漫小说，批判19世纪初英国乡绅阶层。",
            price=12.50,
            env_impact=4,
            image="book3.jpg"
        ),
        Book(
            name_en="Journey to the West",
            name_zh="西游记",
            description_en="A Chinese classic novel about a monk's pilgrimage accompanied by his disciples, including the Monkey King.",
            description_zh="中国古典名著，讲述僧人及孙悟空等徒弟的西天取经之旅。",
            price=15.00,
            env_impact=9,
            image="book4.jpg"
        ),
        Book(
            name_en="To Kill a Mockingbird",
            name_zh="杀死一只知更鸟",
            description_en="Harper Lee's novel about racial injustice in the Deep South, seen through a child's eyes.",
            description_zh="哈珀·李小说，通过孩子视角讲述美国南方的种族不公。",
            price=9.99,
            env_impact=6,
            image="book5.jpg"
        ),
        Book(
            name_en="The Hobbit",
            name_zh="霍比特人",
            description_en="J.R.R. Tolkien's fantasy novel about Bilbo Baggins' adventure in Middle-earth.",
            description_zh="托尔金的奇幻小说，讲述比尔博·巴金斯在中土世界的冒险。",
            price=11.99,
            env_impact=5,
            image="book6.jpg"
        ),
        Book(
            name_en="Moby-Dick",
            name_zh="白鲸记",
            description_en="Herman Melville's epic tale of obsession and revenge on the high seas.",
            description_zh="梅尔维尔史诗般的复仇与执念故事，发生在大海之上。",
            price=13.50,
            env_impact=8,
            image="book7.jpg"
        ),
        Book(
            name_en="War and Peace",
            name_zh="战争与和平",
            description_en="Leo Tolstoy's novel that intertwines the lives of families during the Napoleonic Wars.",
            description_zh="托尔斯泰著作，描写拿破仑战争时期多家庭的命运交织。",
            price=14.99,
            env_impact=10,
            image="book8.jpg"
        )
    ]
    db.session.add_all(books)
    db.session.commit()

    comment1 = Comment(content="Amazing story!", user_id=user.id, book_id=books[0].id)
    comment2 = Comment(content="I Love it！", user_id=user.id, book_id=books[1].id)
    db.session.add_all([comment1, comment2])
    db.session.commit()
