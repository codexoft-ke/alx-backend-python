#!/usr/bin/env python3
"""
Task 2: Concurrent Asynchronous Database Queries
Objective: Run multiple database queries concurrently using asyncio.gather.
"""

import asyncio
import aiosqlite
import time

async def async_fetch_users():
    """
    Asynchronously fetch all users from the database.
    
    Returns:
        list: All users from the database
    """
    print("Starting async_fetch_users...")
    
    async with aiosqlite.connect('users.db') as db:
        cursor = await db.execute("SELECT * FROM users")
        users = await cursor.fetchall()
        await cursor.close()
    
    print(f"async_fetch_users completed - Found {len(users)} users")
    return users

async def async_fetch_older_users():
    """
    Asynchronously fetch users older than 40 from the database.
    
    Returns:
        list: Users older than 40
    """
    print("Starting async_fetch_older_users...")
    
    async with aiosqlite.connect('users.db') as db:
        cursor = await db.execute("SELECT * FROM users WHERE age > ?", (40,))
        older_users = await cursor.fetchall()
        await cursor.close()
    
    print(f"async_fetch_older_users completed - Found {len(older_users)} users older than 40")
    return older_users

async def fetch_concurrently():
    """
    Execute both async functions concurrently using asyncio.gather().
    
    Returns:
        tuple: Results from both async functions
    """
    print("=== Starting Concurrent Database Queries ===\n")
    start_time = time.time()
    
    # Use asyncio.gather to run both queries concurrently
    print("Executing both queries concurrently using asyncio.gather()...")
    all_users, older_users = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    print(f"\n=== Concurrent Execution Completed in {execution_time:.2f} seconds ===")
    
    # Display results
    print(f"\nResults Summary:")
    print(f"- Total users: {len(all_users)}")
    print(f"- Users older than 40: {len(older_users)}")
    
    print(f"\nAll Users:")
    print("-" * 60)
    for user in all_users:
        print(f"ID: {user[0]}, Name: {user[1]}, Email: {user[2]}, Age: {user[3]}")
    
    print(f"\nUsers Older Than 40:")
    print("-" * 60)
    for user in older_users:
        print(f"ID: {user[0]}, Name: {user[1]}, Email: {user[2]}, Age: {user[3]}")
    
    return all_users, older_users

async def demonstrate_performance_benefit():
    """
    Demonstrate the performance benefit of concurrent execution vs sequential execution.
    """
    print("\n" + "="*60)
    print("PERFORMANCE COMPARISON: Concurrent vs Sequential")
    print("="*60)
    
    # Sequential execution
    print("\n1. Sequential Execution:")
    start_time = time.time()
    
    users_seq = await async_fetch_users()
    older_users_seq = await async_fetch_older_users()
    
    sequential_time = time.time() - start_time
    print(f"Sequential execution time: {sequential_time:.4f} seconds")
    
    # Concurrent execution
    print("\n2. Concurrent Execution:")
    start_time = time.time()
    
    users_conc, older_users_conc = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )
    
    concurrent_time = time.time() - start_time
    print(f"Concurrent execution time: {concurrent_time:.4f} seconds")
    
    # Performance improvement
    if sequential_time > concurrent_time:
        improvement = ((sequential_time - concurrent_time) / sequential_time) * 100
        print(f"\nPerformance improvement: {improvement:.1f}% faster with concurrent execution")
    else:
        print(f"\nNote: For this simple example, the difference may be minimal due to database I/O overhead")

def main():
    """
    Main function to run the concurrent fetch operations.
    """
    try:
        # Run the concurrent fetch
        asyncio.run(fetch_concurrently())
        
        # Demonstrate performance benefits
        asyncio.run(demonstrate_performance_benefit())
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
