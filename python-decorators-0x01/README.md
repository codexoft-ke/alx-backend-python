# Python Decorators for Database Operations

This project focuses on mastering Python decorators to enhance database operations in Python applications. Through hands-on tasks, learners will create custom decorators to log queries, handle connections, manage transactions, retry failed operations, and cache query results.

## Learning Objectives

By completing these tasks, professional developers will:

- Deepen their knowledge of Python decorators and how they can be used to create reusable, efficient, and clean code.
- Enhance database management skills by automating repetitive tasks like connection handling, logging, and caching.
- Implement robust transaction management techniques to ensure data integrity and handle errors gracefully.
- Optimize database queries by leveraging caching mechanisms to reduce redundant calls.
- Build resilience into database operations by implementing retry mechanisms for transient errors.
- Apply best practices in database interaction for scalable and maintainable Python applications.

## Requirements

- Python 3.8 or higher installed.
- SQLite3 database setup with a users table for testing.
- A working knowledge of Python decorators and database operations.
- Familiarity with Git and GitHub for project submission.
- Strong problem-solving skills and attention to detail.

## Tasks

### Task 0: Logging Database Queries
Create a decorator to log all SQL queries executed by a function.

### Task 1: Handle Database Connections with a Decorator
Automate database connection handling with a decorator.

### Task 2: Transaction Management Decorator
Implement a decorator to manage database transactions (commit/rollback).

### Task 3: Retry Database Queries
Build a decorator to retry database operations on failure.

### Task 4: Cache Database Queries
Implement a decorator to cache query results.

## Setup

Before running the tasks, make sure to set up the SQLite database with sample data:

```bash
python setup_database.py
```

This will create a `users.db` file with sample user data for testing the decorators.
