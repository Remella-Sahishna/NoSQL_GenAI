# NoSQL Library Management System

A modern, AI-powered library management system built with Flask, MongoDB, and Google Gemini AI. This project demonstrates the power of NoSQL databases combined with modern web technologies and artificial intelligence.

## ✨ Features

- **📚 Book Management**: Add, view, and manage books with detailed information
- **🤖 AI Librarian**: Intelligent chatbot powered by Google Gemini for book recommendations
- **👥 User Management**: User registration and authentication system
- **📖 Book Borrowing**: Track book availability and borrowing system
- **🎨 Modern UI**: Beautiful, responsive design with Bootstrap 5
- **📱 Mobile Friendly**: Optimized for all device sizes
- **🔍 Smart Search**: AI-powered book discovery and recommendations

## 🛠️ Technology Stack

- **Backend**: Flask (Python web framework)
- **Database**: MongoDB (NoSQL database)
- **AI Integration**: Google Gemini AI API
- **Frontend**: HTML5, CSS3, JavaScript
- **UI Framework**: Bootstrap 5
- **Icons**: Font Awesome 6
- **Fonts**: Google Fonts (Poppins)

## 🚀 Installation & Setup

### Prerequisites

- Python 3.8 or higher
- MongoDB installed and running locally
- Google Gemini API key

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd NoSQL_Library
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Set Up MongoDB

1. Install MongoDB on your system
2. Start MongoDB service
3. Create a database named `LibraryDB`

### Step 5: Configure API Keys

1. Get your Google Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Update the API key in `chatbot.py`:
   ```python
   genai.configure(api_key="YOUR_API_KEY_HERE")
   ```

### Step 6: Run the Application

```bash
python chatbot.py
```

The application will be available at `http://localhost:5000`

## 📋 Requirements

Create a `requirements.txt` file with the following dependencies:

```
Flask==3.1.1
Flask-PyMongo==3.0.1
google-generativeai==0.8.5
```

## 🎯 Usage

### 1. User Registration
- Visit the home page
- Fill in your name and email
- Get your unique User ID

### 2. Adding Books
- Login with your User ID
- Navigate to "Add Book"
- Enter book details (title, authors, genres, copies)

### 3. Browsing Books
- View all available books in the library
- See book availability and details
- Access library statistics

### 4. Borrowing Books
- Select from available books
- Complete the borrowing process
- Track your borrowed books

### 5. AI Librarian Chat
- Ask questions about books
- Get personalized recommendations
- Discover new genres and authors

## 🗄️ Database Schema

### Users Collection
```json
{
  "User_id": 1,
  "Username": "John Doe",
  "Email": "john@example.com",
  "borrowed_books": ["Book Title 1", "Book Title 2"]
}
```

### Books Collection
```json
{
  "Book_id": 1,
  "Title": "The Great Gatsby",
  "Authors": ["F. Scott Fitzgerald"],
  "Genres": ["Fiction", "Classic"],
  "Total_copies": 5,
  "Available_copies": 3
}
```

## 🔧 Configuration

### Environment Variables
- `MONGO_URI`: MongoDB connection string (default: `mongodb://localhost:27017/LibraryDB`)
- `SECRET_KEY`: Flask secret key for sessions
- `GEMINI_API_KEY`: Google Gemini API key

### Customization
- Modify colors and styling in `templates/base.html`
- Add new routes in `chatbot.py`
- Extend the database schema as needed

## 🚀 Deployment

### Local Development
```bash
python chatbot.py
```

### Production Deployment
1. Use a production WSGI server (Gunicorn, uWSGI)
2. Set up a reverse proxy (Nginx, Apache)
3. Configure environment variables
4. Set up MongoDB with proper authentication

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- Flask community for the excellent web framework
- MongoDB for the powerful NoSQL database
- Google for the Gemini AI API
- Bootstrap team for the responsive UI framework

## 📞 Support

If you encounter any issues or have questions:

1. Check the existing issues
2. Create a new issue with detailed information
3. Contact the development team

---

**Happy Reading! 📚✨**

