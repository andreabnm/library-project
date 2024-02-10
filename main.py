from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Float, String, Integer


class Base(DeclarativeBase):
    pass


app = Flask(__name__)
db = SQLAlchemy(model_class=Base)
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///new-books-collection.db"
# initialize the app with the extension
db.init_app(app)


class Books(db.Model):
    id: Mapped[id] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)


with app.app_context():
    db.create_all()


@app.route('/')
def home():
    all_books = []
    with app.app_context():
        result = db.session.execute(db.select(Books).order_by(Books.id))
        all_books = result.scalars().all()
    return render_template('index.html', books=all_books)


@app.route("/add", methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        new_book = Books(title=request.form['title'], author=request.form['author'], rating=request.form['rating'])
        with app.app_context():
            db.session.add(new_book)
            db.session.commit()
        return home()
    return render_template('add.html')


@app.route("/edit/<book_id>", methods=['GET', 'POST'])
def edit(book_id):
    with app.app_context():
        book = db.get_or_404(Books, book_id)

    if request.method == 'POST':
        with app.app_context():
            book.rating = request.form['new_rating']
            db.session.commit()
        return home()

    return render_template('edit.html', book=book)


@app.route("/delete")
def delete():
    with app.app_context():
        book = db.get_or_404(Books,  request.args.get('book_id'))
        db.session.delete(book)
        db.session.commit()
    return home()


if __name__ == "__main__":
    app.run(debug=True)
