# Python Context Managers and Async Operations

This project focuses on mastering Python context managers and asynchronous operations for database interactions. Through hands-on tasks, learners will create custom context managers and implement concurrent database operations using asyncio.

## Learning Objectives

By completing these tasks, professional developers will:

- Master the implementation of custom context managers using `__enter__` and `__exit__` methods
- Understand how to manage database connections automatically with context managers
- Learn to create reusable context managers for database query execution
- Implement asynchronous database operations using `aiosqlite`
- Execute concurrent database queries using `asyncio.gather()`
- Apply best practices for resource management and async programming

## Requirements

- Python 3.8 or higher installed
- SQLite3 database setup with a users table for testing
- `aiosqlite` library for asynchronous database operations
- A working knowledge of Python context managers and async/await syntax
- Understanding of database operations and SQL queries

## Tasks

### Task 0: Custom Class-Based Context Manager for Database Connection
Create a class-based context manager to handle opening and closing database connections automatically.

### Task 1: Reusable Query Context Manager
Create a reusable context manager that takes a query as input and executes it, managing both connection and query execution.

### Task 2: Concurrent Asynchronous Database Queries
Run multiple database queries concurrently using `asyncio.gather`.

## Setup

Before running the tasks, make sure to:

1. Install required dependencies:
```bash
pip install aiosqlite
```

2. Set up the SQLite database with sample data:
```bash
python setup_database.py
```

This will create a `users.db` file with sample user data for testing the context managers and async operations.
