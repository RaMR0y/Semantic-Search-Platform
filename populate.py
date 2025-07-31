import asyncio
import asyncpg
from faker import Faker
import random

fake = Faker()

# Sample documents for testing
SAMPLE_DOCUMENTS = [
    {
        "filename": "machine_learning_basics.txt",
        "content": """
        Machine Learning Fundamentals
        
        Machine learning is a subset of artificial intelligence that enables computers to learn and make decisions without being explicitly programmed. There are three main types of machine learning: supervised learning, unsupervised learning, and reinforcement learning.
        
        Supervised learning involves training a model on labeled data, where the correct answers are provided. Common algorithms include linear regression, logistic regression, decision trees, and neural networks. These models can predict outcomes based on input features.
        
        Unsupervised learning works with unlabeled data to find hidden patterns and structures. Clustering algorithms like K-means and dimensionality reduction techniques like PCA are examples of unsupervised learning methods.
        
        Reinforcement learning is about training agents to make sequences of decisions by rewarding good actions and penalizing bad ones. This approach is commonly used in game playing, robotics, and autonomous systems.
        
        The machine learning workflow typically involves data collection, preprocessing, feature engineering, model selection, training, evaluation, and deployment. Data quality and quantity are crucial factors that determine the success of any machine learning project.
        """
    },
    {
        "filename": "python_programming.txt",
        "content": """
        Python Programming Guide
        
        Python is a high-level, interpreted programming language known for its simplicity and readability. It was created by Guido van Rossum and first released in 1991. Python supports multiple programming paradigms including procedural, object-oriented, and functional programming.
        
        Key features of Python include dynamic typing, automatic memory management, and extensive standard libraries. The language emphasizes code readability with its use of significant whitespace and clear syntax. Python's "batteries included" philosophy means that many common programming tasks are already implemented in the standard library.
        
        Python is widely used in web development, data science, artificial intelligence, scientific computing, and automation. Popular frameworks include Django and Flask for web development, NumPy and Pandas for data analysis, and TensorFlow and PyTorch for machine learning.
        
        The Python Package Index (PyPI) contains over 300,000 packages, making it easy to find and install additional functionality. Virtual environments help manage dependencies and avoid conflicts between different projects.
        
        Python's syntax is designed to be intuitive and readable, making it an excellent choice for beginners and experienced developers alike. The language's extensive documentation and active community provide excellent support for learning and problem-solving.
        """
    },
    {
        "filename": "database_design.txt",
        "content": """
        Database Design Principles
        
        Database design is the process of creating a detailed data model of a database. This logical design determines how data is stored, organized, and accessed. Good database design is crucial for ensuring data integrity, performance, and scalability.
        
        The relational database model, developed by E.F. Codd, organizes data into tables with rows and columns. Each table represents an entity, and relationships between entities are established through foreign keys. Normalization is a process that reduces data redundancy and improves data integrity by organizing data into related tables.
        
        Key concepts in database design include entities, attributes, relationships, and constraints. Entities are objects or concepts about which data is collected, such as customers, products, or orders. Attributes are properties of entities, such as customer name, product price, or order date.
        
        Relationships define how entities are connected to each other. Common relationship types include one-to-one, one-to-many, and many-to-many. Constraints ensure data integrity by enforcing rules about what data can be stored in the database.
        
        Indexing is crucial for database performance. Indexes speed up data retrieval by creating pointers to data locations. However, too many indexes can slow down write operations, so a balance must be struck between read and write performance.
        """
    },
    {
        "filename": "api_design.txt",
        "content": """
        RESTful API Design Guidelines
        
        REST (Representational State Transfer) is an architectural style for designing networked applications. RESTful APIs use HTTP methods to perform operations on resources, making them stateless and cacheable. The design principles focus on simplicity, scalability, and reliability.
        
        HTTP methods map to CRUD operations: GET for reading, POST for creating, PUT for updating, and DELETE for removing resources. Resource URLs should be nouns, not verbs, and follow a hierarchical structure. For example, /users/123/orders represents orders belonging to user 123.
        
        Status codes provide information about the success or failure of requests. 2xx codes indicate success, 4xx codes indicate client errors, and 5xx codes indicate server errors. Common status codes include 200 (OK), 201 (Created), 400 (Bad Request), 404 (Not Found), and 500 (Internal Server Error).
        
        API versioning is important for maintaining backward compatibility. Versioning can be done through URL paths (/api/v1/users), query parameters (/api/users?version=1), or HTTP headers. Documentation is essential for API adoption and should include examples, error responses, and authentication methods.
        
        Security considerations include authentication, authorization, input validation, and rate limiting. HTTPS should be used for all API communications to encrypt data in transit. API keys, OAuth tokens, and JWT tokens are common authentication methods.
        """
    },
    {
        "filename": "cloud_computing.txt",
        "content": """
        Cloud Computing Fundamentals
        
        Cloud computing is the delivery of computing services over the internet, including servers, storage, databases, networking, software, and analytics. Instead of owning and maintaining physical infrastructure, organizations can access these resources on-demand from cloud providers.
        
        There are three main service models: Infrastructure as a Service (IaaS), Platform as a Service (PaaS), and Software as a Service (SaaS). IaaS provides virtualized computing resources, PaaS offers development platforms, and SaaS delivers software applications over the internet.
        
        Cloud deployment models include public, private, hybrid, and multi-cloud. Public clouds are owned by third-party providers and available to the general public. Private clouds are used exclusively by a single organization. Hybrid clouds combine public and private cloud resources.
        
        Key benefits of cloud computing include cost savings, scalability, flexibility, and disaster recovery. Organizations can pay only for the resources they use, scale up or down based on demand, and access resources from anywhere with an internet connection.
        
        Security and compliance are critical considerations in cloud computing. Cloud providers implement various security measures, but organizations are responsible for securing their applications and data. Regular backups, encryption, and access controls are essential for protecting cloud resources.
        """
    }
]

async def populate_database():
    """Populate database with sample documents and embeddings"""
    # Connect to database
    conn = await asyncpg.connect(
        user="appuser",
        password="apppass",
        database="semsearch",
        host="localhost"
    )
    
    try:
        print("Starting database population...")
        
        # Clear existing data
        await conn.execute("DELETE FROM responses")
        await conn.execute("DELETE FROM queries")
        await conn.execute("DELETE FROM embeddings")
        await conn.execute("DELETE FROM documents")
        
        # Insert sample documents
        for doc in SAMPLE_DOCUMENTS:
            print(f"Inserting document: {doc['filename']}")
            
            # Insert document
            document_record = await conn.fetchrow(
                "INSERT INTO documents (filename, content) VALUES ($1, $2) RETURNING id",
                doc['filename'], doc['content']
            )
            document_id = document_record['id']
            
            # Generate dummy embeddings (in real app, these would be actual embeddings)
            # For testing, we'll create random vectors
            chunks = doc['content'].split('\n\n')
            for i, chunk in enumerate(chunks):
                if chunk.strip():  # Skip empty chunks
                    # Generate random vector (384 dimensions for all-MiniLM-L6-v2)
                    vector = [random.uniform(-1, 1) for _ in range(384)]
                    
                    await conn.execute(
                        "INSERT INTO embeddings (document_id, chunk_index, chunk_text, vector) VALUES ($1, $2, $3, $4)",
                        document_id, i, chunk.strip(), vector
                    )
        
        # Verify data
        doc_count = await conn.fetchval("SELECT COUNT(*) FROM documents")
        embedding_count = await conn.fetchval("SELECT COUNT(*) FROM embeddings")
        
        print(f"Database populated successfully!")
        print(f"Documents: {doc_count}")
        print(f"Embeddings: {embedding_count}")
        
    except Exception as e:
        print(f"Error populating database: {e}")
        raise
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(populate_database()) 