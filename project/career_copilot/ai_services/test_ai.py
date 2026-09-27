"""
Test AI service - generates assessment questions and evaluates tests.
"""
import json
import random
from .openai_service import AIService


# Question banks by skill
TEST_BANKS = {
    'python': [
        {'question': 'What is the output of: print(type([]))?', 'options': ["<class 'list'>", "<class 'array'>", "<class 'tuple'>", "<class 'dict'>"], 'correct': 0, 'topic': 'Data Types'},
        {'question': 'Which keyword is used to define a function in Python?', 'options': ['function', 'def', 'func', 'define'], 'correct': 1, 'topic': 'Functions'},
        {'question': 'What does len("hello") return?', 'options': ['4', '5', '6', 'Error'], 'correct': 1, 'topic': 'Strings'},
        {'question': 'Which of the following is immutable in Python?', 'options': ['list', 'dict', 'set', 'tuple'], 'correct': 3, 'topic': 'Data Types'},
        {'question': 'What is the result of 2 ** 3 in Python?', 'options': ['6', '8', '23', 'Error'], 'correct': 1, 'topic': 'Operators'},
        {'question': 'Which method adds an element to the end of a list?', 'options': ['add()', 'append()', 'insert()', 'extend()'], 'correct': 1, 'topic': 'Lists'},
        {'question': 'What does the range(5) produce?', 'options': ['[1, 2, 3, 4, 5]', '[0, 1, 2, 3, 4]', '[0, 1, 2, 3, 4, 5]', '[1, 2, 3, 4]'], 'correct': 1, 'topic': 'Loops'},
        {'question': 'Which is the correct way to create a dictionary?', 'options': ['dict = []', 'dict = {}', 'dict = ()', 'dict = set()'], 'correct': 1, 'topic': 'Dictionaries'},
        {'question': 'What is list comprehension syntax?', 'options': ['[x for x in y]', 'for x in y: [x]', '[x in y]', 'list(x for y)'], 'correct': 0, 'topic': 'Lists'},
        {'question': 'What does the __init__ method do?', 'options': ['Initializes a module', 'Initializes an object', 'Imports a library', 'Defines a variable'], 'correct': 1, 'topic': 'OOP'},
        {'question': 'Which keyword handles exceptions?', 'options': ['catch', 'except', 'handle', 'rescue'], 'correct': 1, 'topic': 'Exceptions'},
        {'question': 'What is a lambda function?', 'options': ['A named function', 'An anonymous function', 'A recursive function', 'A built-in function'], 'correct': 1, 'topic': 'Functions'},
        {'question': 'How do you comment a single line in Python?', 'options': ['// comment', '/* comment */', '# comment', '<!-- comment -->'], 'correct': 2, 'topic': 'Basics'},
        {'question': 'What does the split() method do?', 'options': ['Joins strings', 'Splits a string into a list', 'Sorts a list', 'Slices a list'], 'correct': 1, 'topic': 'Strings'},
        {'question': 'Which is NOT a Python data type?', 'options': ['int', 'float', 'char', 'bool'], 'correct': 2, 'topic': 'Data Types'},
    ],
    'sql': [
        {'question': 'Which SQL statement is used to retrieve data?', 'options': ['GET', 'SELECT', 'FETCH', 'RETRIEVE'], 'correct': 1, 'topic': 'Basics'},
        {'question': 'Which clause filters rows in SQL?', 'options': ['WHERE', 'FILTER', 'HAVING', 'GROUP BY'], 'correct': 0, 'topic': 'Querying'},
        {'question': 'What does JOIN do?', 'options': ['Combines rows from two tables', 'Adds a new row', 'Creates a table', 'Updates data'], 'correct': 0, 'topic': 'Joins'},
        {'question': 'Which JOIN returns all rows from both tables?', 'options': ['INNER JOIN', 'LEFT JOIN', 'RIGHT JOIN', 'FULL OUTER JOIN'], 'correct': 3, 'topic': 'Joins'},
        {'question': 'What does GROUP BY do?', 'options': ['Sorts results', 'Groups rows with same values', 'Counts rows', 'Filters data'], 'correct': 1, 'topic': 'Aggregation'},
        {'question': 'Which is an aggregate function?', 'options': ['COUNT', 'GROUP', 'SORT', 'FILTER'], 'correct': 0, 'topic': 'Aggregation'},
        {'question': 'What does HAVING do?', 'options': ['Filters before grouping', 'Filters after grouping', 'Orders results', 'Limits results'], 'correct': 1, 'topic': 'Aggregation'},
        {'question': 'Which keyword sorts results?', 'options': ['SORT', 'ORDER BY', 'ARRANGE', 'GROUP BY'], 'correct': 1, 'topic': 'Querying'},
        {'question': 'What is a primary key?', 'options': ['A unique identifier for rows', 'A foreign reference', 'An index', 'A constraint'], 'correct': 0, 'topic': 'Schema'},
        {'question': 'What does DISTINCT do?', 'options': ['Removes duplicates', 'Counts rows', 'Orders data', 'Filters data'], 'correct': 0, 'topic': 'Querying'},
        {'question': 'Which is used for pattern matching?', 'options': ['MATCH', 'LIKE', 'SIMILAR', 'SEARCH'], 'correct': 1, 'topic': 'Querying'},
        {'question': 'What does NULL mean in SQL?', 'options': ['Zero', 'Empty string', 'Missing/unknown value', 'False'], 'correct': 2, 'topic': 'Basics'},
        {'question': 'Which command adds a new row?', 'options': ['ADD', 'INSERT', 'CREATE', 'APPEND'], 'correct': 1, 'topic': 'DML'},
        {'question': 'What is normalization?', 'options': ['Organizing data to reduce redundancy', 'Sorting data alphabetically', 'Compressing the database', 'Encrypting data'], 'correct': 0, 'topic': 'Schema'},
        {'question': 'Which is a subquery?', 'options': ['A query inside another query', 'A backup query', 'A stored procedure', 'A view'], 'correct': 0, 'topic': 'Advanced'},
    ],
    'java': [
        {'question': 'Which is NOT a primitive type in Java?', 'options': ['int', 'String', 'boolean', 'char'], 'correct': 1, 'topic': 'Basics'},
        {'question': 'What is the entry point of a Java program?', 'options': ['start()', 'main()', 'run()', 'init()'], 'correct': 1, 'topic': 'Basics'},
        {'question': 'Which keyword creates an object?', 'options': ['create', 'new', 'make', 'instantiate'], 'correct': 1, 'topic': 'OOP'},
        {'question': 'What does final mean for a variable?', 'options': ['Cannot be changed', 'Is private', 'Is static', 'Is public'], 'correct': 0, 'topic': 'Keywords'},
        {'question': 'Which is a marker interface?', 'options': ['Runnable', 'Serializable', 'Comparable', 'Iterator'], 'correct': 1, 'topic': 'Interfaces'},
        {'question': 'What is JVM?', 'options': ['Java Virtual Machine', 'Java Variable Method', 'Java Verification Module', 'Java Visual Manager'], 'correct': 0, 'topic': 'JVM'},
        {'question': 'Which collection allows duplicates?', 'options': ['Set', 'List', 'Map', 'Queue'], 'correct': 1, 'topic': 'Collections'},
        {'question': 'What does static mean?', 'options': ['Belongs to the class', 'Cannot be changed', 'Is private', 'Is constant'], 'correct': 0, 'topic': 'Keywords'},
        {'question': 'Which keyword is used for inheritance?', 'options': ['inherits', 'extends', 'implements', 'uses'], 'correct': 1, 'topic': 'OOP'},
        {'question': 'What is autoboxing?', 'options': ['Converting primitives to wrappers', 'Boxing objects', 'Creating arrays', 'Wrapping methods'], 'correct': 0, 'topic': 'Advanced'},
        {'question': 'Which is used for exception handling?', 'options': ['try-catch', 'if-else', 'switch', 'for'], 'correct': 0, 'topic': 'Exceptions'},
        {'question': 'What is the parent class of all classes?', 'options': ['Class', 'Object', 'Super', 'Parent'], 'correct': 1, 'topic': 'OOP'},
        {'question': 'Which keyword prevents method overriding?', 'options': ['static', 'final', 'private', 'sealed'], 'correct': 1, 'topic': 'Keywords'},
        {'question': 'What is polymorphism?', 'options': ['Many forms', 'Single form', 'No form', 'Static form'], 'correct': 0, 'topic': 'OOP'},
        {'question': 'Which is used for multi-threading?', 'options': ['Thread class', 'Array class', 'String class', 'Math class'], 'correct': 0, 'topic': 'Concurrency'},
    ],
    'javascript': [
        {'question': 'What is the output of: typeof null?', 'options': ['null', 'undefined', 'object', 'number'], 'correct': 2, 'topic': 'Types'},
        {'question': 'Which keyword declares a block-scoped variable?', 'options': ['var', 'let', 'function', 'static'], 'correct': 1, 'topic': 'Variables'},
        {'question': 'What does === check?', 'options': ['Value only', 'Type only', 'Value and type', 'Reference only'], 'correct': 2, 'topic': 'Operators'},
        {'question': 'What is a closure?', 'options': ['A function with access to outer scope', 'A sealed object', 'A private method', 'A loop construct'], 'correct': 0, 'topic': 'Functions'},
        {'question': 'Which method adds to end of array?', 'options': ['add()', 'push()', 'append()', 'insert()'], 'correct': 1, 'topic': 'Arrays'},
        {'question': 'What does async/await handle?', 'options': ['Loops', 'Promises', 'Arrays', 'Objects'], 'correct': 1, 'topic': 'Async'},
        {'question': 'What is hoisting?', 'options': ['Moving declarations to top', 'Sorting arrays', 'Lifting objects', 'Stacking calls'], 'correct': 0, 'topic': 'Basics'},
        {'question': 'Which is NOT a JavaScript framework?', 'options': ['React', 'Angular', 'Vue', 'Django'], 'correct': 3, 'topic': 'Ecosystem'},
        {'question': 'What does map() do?', 'options': ['Filters elements', 'Transforms each element', 'Sorts elements', 'Reduces elements'], 'correct': 1, 'topic': 'Arrays'},
        {'question': 'What is the event loop?', 'options': ['A loop for events', 'JS concurrency model', 'A DOM feature', 'A CSS feature'], 'correct': 1, 'topic': 'Async'},
        {'question': 'Which keyword defines a constant?', 'options': ['const', 'final', 'static', 'fixed'], 'correct': 0, 'topic': 'Variables'},
        {'question': 'What is JSON?', 'options': ['JavaScript Object Notation', 'Java Standard Object', 'JavaScript Online Notation', 'Just Some Object Name'], 'correct': 0, 'topic': 'Basics'},
        {'question': 'What does this refer to in arrow functions?', 'options': ['The function itself', 'The enclosing scope', 'The global object', 'undefined'], 'correct': 1, 'topic': 'Functions'},
        {'question': 'What is a Promise?', 'options': ['A guarantee', 'An async value', 'A callback', 'A loop'], 'correct': 1, 'topic': 'Async'},
        {'question': 'Which method converts JSON to object?', 'options': ['JSON.parse()', 'JSON.stringify()', 'JSON.toObject()', 'JSON.convert()'], 'correct': 0, 'topic': 'Basics'},
    ],
    'data structures': [
        {'question': 'What is the time complexity of binary search?', 'options': ['O(n)', 'O(log n)', 'O(n^2)', 'O(1)'], 'correct': 1, 'topic': 'Algorithms'},
        {'question': 'Which data structure uses LIFO?', 'options': ['Queue', 'Stack', 'Array', 'Linked List'], 'correct': 1, 'topic': 'Stacks'},
        {'question': 'Which data structure uses FIFO?', 'options': ['Queue', 'Stack', 'Tree', 'Graph'], 'correct': 0, 'topic': 'Queues'},
        {'question': 'What is the height of a balanced BST with n nodes?', 'options': ['O(n)', 'O(log n)', 'O(n log n)', 'O(1)'], 'correct': 1, 'topic': 'Trees'},
        {'question': 'Which is NOT a linear data structure?', 'options': ['Array', 'Linked List', 'Tree', 'Queue'], 'correct': 2, 'topic': 'Basics'},
        {'question': 'What is a hash table?', 'options': ['Key-value store with hashing', 'Sorted array', 'Tree structure', 'Linked list'], 'correct': 0, 'topic': 'Hashing'},
        {'question': 'What is the time complexity of inserting at head of linked list?', 'options': ['O(n)', 'O(1)', 'O(log n)', 'O(n^2)'], 'correct': 1, 'topic': 'Linked Lists'},
        {'question': 'Which traversal visits root, left, right?', 'options': ['Inorder', 'Preorder', 'Postorder', 'Level order'], 'correct': 1, 'topic': 'Trees'},
        {'question': 'What is a graph?', 'options': ['Nodes and edges', 'A tree', 'A sorted list', 'A hash map'], 'correct': 0, 'topic': 'Graphs'},
        {'question': 'Which sorting algorithm is O(n log n) on average?', 'options': ['Bubble', 'Selection', 'Merge Sort', 'Insertion'], 'correct': 2, 'topic': 'Algorithms'},
        {'question': 'What is a priority queue?', 'options': ['FIFO queue', 'LIFO stack', 'Elements ordered by priority', 'A hash map'], 'correct': 2, 'topic': 'Queues'},
        {'question': 'What is amortized analysis?', 'options': ['Average over operations', 'Worst case', 'Best case', 'Space analysis'], 'correct': 0, 'topic': 'Algorithms'},
        {'question': 'What is dynamic programming?', 'options': ['Breaking into subproblems', 'Random programming', 'Runtime programming', 'Static programming'], 'correct': 0, 'topic': 'Algorithms'},
        {'question': 'What is the space complexity of recursion?', 'options': ['O(1)', 'O(n) stack space', 'O(log n)', 'O(n^2)'], 'correct': 1, 'topic': 'Algorithms'},
        {'question': 'What is a doubly linked list?', 'options': ['One direction', 'Two directions', 'Circular', 'A tree'], 'correct': 1, 'topic': 'Linked Lists'},
    ],
    'html': [
        {'question': 'What does HTML stand for?', 'options': ['Hyper Text Markup Language', 'High Text Machine Language', 'Hyper Tabular Markup Language', 'None'], 'correct': 0, 'topic': 'Basics'},
        {'question': 'Which tag creates a hyperlink?', 'options': ['<link>', '<a>', '<href>', '<url>'], 'correct': 1, 'topic': 'Tags'},
        {'question': 'Which tag creates a list item?', 'options': ['<list>', '<item>', '<li>', '<ul>'], 'correct': 2, 'topic': 'Tags'},
        {'question': 'What is the correct DOCTYPE for HTML5?', 'options': ['<!DOCTYPE HTML5>', '<!DOCTYPE html>', '<DOCTYPE>', '<!HTML5>'], 'correct': 1, 'topic': 'Basics'},
        {'question': 'Which tag is used for the largest heading?', 'options': ['<head>', '<h6>', '<h1>', '<header>'], 'correct': 2, 'topic': 'Tags'},
        {'question': 'Which attribute specifies alternative text?', 'options': ['title', 'alt', 'src', 'desc'], 'correct': 1, 'topic': 'Attributes'},
        {'question': 'Which tag creates a table row?', 'options': ['<row>', '<tr>', '<td>', '<th>'], 'correct': 1, 'topic': 'Tables'},
        {'question': 'Which input type creates a checkbox?', 'options': ['check', 'checkbox', 'tick', 'select'], 'correct': 1, 'topic': 'Forms'},
        {'question': 'What does the <meta> tag do?', 'options': ['Defines metadata', 'Creates links', 'Styles content', 'Adds scripts'], 'correct': 0, 'topic': 'Tags'},
        {'question': 'Which tag creates a form?', 'options': ['<form>', '<input>', '<field>', '<submit>'], 'correct': 0, 'topic': 'Forms'},
    ],
    'css': [
        {'question': 'What does CSS stand for?', 'options': ['Computer Style Sheets', 'Cascading Style Sheets', 'Creative Style Sheets', 'Colorful Style Sheets'], 'correct': 1, 'topic': 'Basics'},
        {'question': 'Which property changes text color?', 'options': ['text-color', 'color', 'font-color', 'text-style'], 'correct': 1, 'topic': 'Properties'},
        {'question': 'How do you select an element with id "demo"?', 'options': ['.demo', '#demo', 'demo', '*demo'], 'correct': 1, 'topic': 'Selectors'},
        {'question': 'Which display value makes elements inline with block features?', 'options': ['inline', 'block', 'inline-block', 'flex'], 'correct': 2, 'topic': 'Layout'},
        {'question': 'What does flexbox do?', 'options': ['Creates flexible layouts', 'Adds shadows', 'Changes fonts', 'Creates animations'], 'correct': 0, 'topic': 'Layout'},
        {'question': 'Which property adds spacing inside an element?', 'options': ['margin', 'padding', 'spacing', 'border'], 'correct': 1, 'topic': 'Box Model'},
        {'question': 'What is the z-index property for?', 'options': ['Zoom', 'Stacking order', 'Font size', 'Opacity'], 'correct': 1, 'topic': 'Positioning'},
        {'question': 'Which unit is relative to the parent font size?', 'options': ['px', 'em', 'rem', 'vh'], 'correct': 1, 'topic': 'Units'},
        {'question': 'What does position: absolute do?', 'options': ['Fixes to viewport', 'Positions relative to nearest positioned ancestor', 'Stays in flow', 'Hides element'], 'correct': 1, 'topic': 'Positioning'},
        {'question': 'Which property creates rounded corners?', 'options': ['border-radius', 'corner-radius', 'round-corner', 'border-round'], 'correct': 0, 'topic': 'Properties'},
    ],
    'dbms': [
        {'question': 'What is DBMS?', 'options': ['Database Management System', 'Data Backup Management System', 'Database Monitoring System', 'Data Base Multi System'], 'correct': 0, 'topic': 'Basics'},
        {'question': 'Which is a type of DBMS?', 'options': ['Hierarchical', 'Network', 'Relational', 'All of the above'], 'correct': 3, 'topic': 'Types'},
        {'question': 'What is ACID?', 'options': ['Atomicity, Consistency, Isolation, Durability', 'A Computer Interface Design', 'Application Cache Interface Driver', 'Auto Commit Isolation Data'], 'correct': 0, 'topic': 'Transactions'},
        {'question': 'What is a foreign key?', 'options': ['A key from another table', 'A primary key', 'An index', 'A constraint'], 'correct': 0, 'topic': 'Schema'},
        {'question': 'What is denormalization?', 'options': ['Adding redundancy for performance', 'Removing redundancy', 'Encrypting data', 'Compressing data'], 'correct': 0, 'topic': 'Design'},
        {'question': 'What is a view?', 'options': ['A virtual table', 'A stored procedure', 'A trigger', 'An index'], 'correct': 0, 'topic': 'Objects'},
        {'question': 'What is an index?', 'options': ['Speeds up data retrieval', 'Stores data', 'Creates backups', 'Manages transactions'], 'correct': 0, 'topic': 'Performance'},
        {'question': 'What is a trigger?', 'options': ['Auto-executed code on events', 'A stored query', 'A backup', 'A constraint'], 'correct': 0, 'topic': 'Advanced'},
        {'question': 'What is a stored procedure?', 'options': ['Pre-compiled SQL code', 'A view', 'An index', 'A trigger'], 'correct': 0, 'topic': 'Advanced'},
        {'question': 'What is a cursor?', 'options': ['Iterates over result rows', 'A pointer to a table', 'A type of join', 'A constraint'], 'correct': 0, 'topic': 'Advanced'},
    ],
    'operating systems': [
        {'question': 'What is an operating system?', 'options': ['System software managing hardware', 'A programming language', 'A web browser', 'A database'], 'correct': 0, 'topic': 'Basics'},
        {'question': 'What is a process?', 'options': ['A program in execution', 'A file', 'A thread', 'A socket'], 'correct': 0, 'topic': 'Processes'},
        {'question': 'What is scheduling?', 'options': ['Deciding process execution order', 'Sorting files', 'Managing memory', 'Handling I/O'], 'correct': 0, 'topic': 'Scheduling'},
        {'question': 'What is deadlock?', 'options': ['Processes waiting indefinitely', 'A crash', 'A memory leak', 'A slow process'], 'correct': 0, 'topic': 'Concurrency'},
        {'question': 'What is virtual memory?', 'options': ['Memory on disk extending RAM', 'RAM only', 'Cache memory', 'ROM'], 'correct': 0, 'topic': 'Memory'},
        {'question': 'What is a thread?', 'options': ['A unit of execution within a process', 'A process', 'A file', 'A socket'], 'correct': 0, 'topic': 'Threads'},
        {'question': 'What is paging?', 'options': ['Dividing memory into fixed-size blocks', 'Dividing CPU time', 'Managing files', 'Handling I/O'], 'correct': 0, 'topic': 'Memory'},
        {'question': 'What is a system call?', 'options': ['Request to OS kernel', 'A function call', 'A hardware interrupt', 'A signal'], 'correct': 0, 'topic': 'Kernel'},
        {'question': 'What is context switching?', 'options': ['Saving and restoring process state', 'Changing users', 'Switching files', 'Updating OS'], 'correct': 0, 'topic': 'Processes'},
        {'question': 'What is thrashing?', 'options': ['Excessive paging degrading performance', 'A crash', 'Memory corruption', 'CPU overheating'], 'correct': 0, 'topic': 'Memory'},
    ],
    'computer networks': [
        {'question': 'What is OSI model?', 'options': ['7-layer network model', 'A protocol', 'A hardware device', 'A programming language'], 'correct': 0, 'topic': 'Models'},
        {'question': 'How many layers in OSI model?', 'options': ['5', '6', '7', '8'], 'correct': 2, 'topic': 'Models'},
        {'question': 'What is TCP?', 'options': ['Connection-oriented protocol', 'Connectionless protocol', 'A routing protocol', 'A hardware device'], 'correct': 0, 'topic': 'Protocols'},
        {'question': 'What is UDP?', 'options': ['Connectionless protocol', 'Connection-oriented', 'Reliable', 'Ordered'], 'correct': 0, 'topic': 'Protocols'},
        {'question': 'What is an IP address?', 'options': ['Unique network identifier', 'A password', 'A port number', 'A protocol'], 'correct': 0, 'topic': 'Addressing'},
        {'question': 'What is DNS?', 'options': ['Domain Name System', 'Data Network Service', 'Direct Network System', 'Domain Network Service'], 'correct': 0, 'topic': 'Services'},
        {'question': 'What is a subnet mask?', 'options': ['Divides network and host', 'Encrypts data', 'Routes packets', 'Blocks traffic'], 'correct': 0, 'topic': 'Addressing'},
        {'question': 'What is HTTP?', 'options': ['HyperText Transfer Protocol', 'High Transfer Text Protocol', 'HyperText Transmission Protocol', 'Host Transfer Protocol'], 'correct': 0, 'topic': 'Protocols'},
        {'question': 'What is a firewall?', 'options': ['Network security barrier', 'A hardware device only', 'A protocol', 'A type of cable'], 'correct': 0, 'topic': 'Security'},
        {'question': 'What is bandwidth?', 'options': ['Data transfer capacity', 'Network speed limit', 'Cable width', 'Signal strength'], 'correct': 0, 'topic': 'Basics'},
    ],
    'machine learning': [
        {'question': 'What is supervised learning?', 'options': ['Learning with labeled data', 'Learning without labels', 'Learning by reinforcement', 'Unsupervised clustering'], 'correct': 0, 'topic': 'Types'},
        {'question': 'What is overfitting?', 'options': ['Model memorizes training data', 'Model is too simple', 'Model is perfect', 'No learning occurs'], 'correct': 0, 'topic': 'Concepts'},
        {'question': 'What is a neural network?', 'options': ['Layers of interconnected nodes', 'A brain', 'A single neuron', 'A decision tree'], 'correct': 0, 'topic': 'Deep Learning'},
        {'question': 'What is gradient descent?', 'options': ['Optimization algorithm', 'A loss function', 'A neural network', 'A dataset'], 'correct': 0, 'topic': 'Optimization'},
        {'question': 'What is cross-validation?', 'options': ['Model evaluation technique', 'Data preprocessing', 'Feature selection', 'A loss function'], 'correct': 0, 'topic': 'Evaluation'},
        {'question': 'What is regularization?', 'options': ['Prevents overfitting', 'Speeds up training', 'Increases model complexity', 'Adds layers'], 'correct': 0, 'topic': 'Techniques'},
        {'question': 'What is a confusion matrix?', 'options': ['Classification performance table', 'A neural network', 'A data structure', 'A loss function'], 'correct': 0, 'topic': 'Evaluation'},
        {'question': 'What is PCA?', 'options': ['Dimensionality reduction', 'A classifier', 'A clustering algorithm', 'A neural network'], 'correct': 0, 'topic': 'Techniques'},
        {'question': 'What is K-means?', 'options': ['Clustering algorithm', 'Classification algorithm', 'Regression technique', 'A neural network'], 'correct': 0, 'topic': 'Algorithms'},
        {'question': 'What is a learning rate?', 'options': ['Step size in gradient descent', 'Speed of training', 'Model accuracy', 'Dataset size'], 'correct': 0, 'topic': 'Optimization'},
    ],
    'c': [
        {'question': 'Which header file is needed for printf?', 'options': ['<stdlib.h>', '<stdio.h>', '<string.h>', '<math.h>'], 'correct': 1, 'topic': 'Basics'},
        {'question': 'What is a pointer?', 'options': ['A variable storing an address', 'A function', 'A data type', 'A loop'], 'correct': 0, 'topic': 'Pointers'},
        {'question': 'Which is used to allocate memory dynamically?', 'options': ['alloc()', 'malloc()', 'create()', 'new()'], 'correct': 1, 'topic': 'Memory'},
        {'question': 'What is the size of int in C (typically)?', 'options': ['2 bytes', '4 bytes', '8 bytes', 'Depends on system'], 'correct': 3, 'topic': 'Data Types'},
        {'question': 'Which keyword defines a constant?', 'options': ['const', 'final', 'static', 'fixed'], 'correct': 0, 'topic': 'Keywords'},
        {'question': 'What does sizeof() return?', 'options': ['Size in bytes', 'Number of elements', 'Address', 'Value'], 'correct': 0, 'topic': 'Operators'},
        {'question': 'Which is a string function?', 'options': ['strlen()', 'length()', 'size()', 'count()'], 'correct': 0, 'topic': 'Strings'},
        {'question': 'What is a struct?', 'options': ['A custom data type', 'A function', 'A loop', 'A pointer'], 'correct': 0, 'topic': 'Structures'},
        {'question': 'Which operator accesses struct members via pointer?', 'options': ['.', '->', '::', ':'], 'correct': 1, 'topic': 'Pointers'},
        {'question': 'What does free() do?', 'options': ['Releases allocated memory', 'Deletes a file', 'Clears the screen', 'Resets variables'], 'correct': 0, 'topic': 'Memory'},
    ],
    # ─── Non-CSE domains ───────────────────────────────────────────────────────
    'thermodynamics': [
        {'question': 'Which law of thermodynamics states energy cannot be created or destroyed?', 'options': ['Zeroth Law', 'First Law', 'Second Law', 'Third Law'], 'correct': 1, 'topic': 'Laws'},
        {'question': 'What is the unit of entropy?', 'options': ['J/K', 'J/kg', 'W/m²', 'Pa'], 'correct': 0, 'topic': 'Entropy'},
        {'question': 'Which thermodynamic cycle is used in petrol engines?', 'options': ['Rankine cycle', 'Diesel cycle', 'Otto cycle', 'Carnot cycle'], 'correct': 2, 'topic': 'Cycles'},
        {'question': 'What is the efficiency of a Carnot engine operating between 500K and 300K?', 'options': ['40%', '50%', '60%', '70%'], 'correct': 0, 'topic': 'Efficiency'},
        {'question': 'Which process occurs at constant pressure?', 'options': ['Isochoric', 'Isobaric', 'Isothermal', 'Adiabatic'], 'correct': 1, 'topic': 'Processes'},
        {'question': 'What does the second law of thermodynamics state?', 'options': ['Energy is conserved', 'Entropy of isolated systems tends to increase', 'Temperature cannot reach absolute zero', 'Heat flows from cold to hot'], 'correct': 1, 'topic': 'Laws'},
        {'question': 'Which heat transfer mode does not require a medium?', 'options': ['Conduction', 'Convection', 'Radiation', 'All require medium'], 'correct': 2, 'topic': 'Heat Transfer'},
        {'question': 'In a Rankine cycle, what does the turbine produce?', 'options': ['Heat', 'Work output', 'Entropy', 'Pressure'], 'correct': 1, 'topic': 'Cycles'},
        {'question': 'What is enthalpy?', 'options': ['H = U + PV', 'H = U - PV', 'H = U + TV', 'H = PV - U'], 'correct': 0, 'topic': 'Properties'},
        {'question': 'Which gas law relates P, V, and T for ideal gases?', 'options': ['Dalton\'s Law', 'Boyle\'s Law', 'Ideal Gas Law (PV = nRT)', 'Henry\'s Law'], 'correct': 2, 'topic': 'Gas Laws'},
        {'question': 'What is Fourier\'s law used for?', 'options': ['Fluid flow', 'Heat conduction', 'Radiation', 'Convection'], 'correct': 1, 'topic': 'Heat Transfer'},
        {'question': 'In which cycle does heat addition occur at constant volume?', 'options': ['Brayton', 'Rankine', 'Otto', 'Diesel'], 'correct': 2, 'topic': 'Cycles'},
        {'question': 'What is COP (Coefficient of Performance)?', 'options': ['Useful heat / Work input', 'Work output / Heat input', 'Entropy change / Temperature', 'None'], 'correct': 0, 'topic': 'Refrigeration'},
        {'question': 'Which thermodynamic property remains constant in an isothermal process?', 'options': ['Pressure', 'Volume', 'Temperature', 'Entropy'], 'correct': 2, 'topic': 'Processes'},
        {'question': 'What does the zeroth law of thermodynamics define?', 'options': ['Energy conservation', 'Thermal equilibrium and temperature', 'Entropy', 'Absolute zero'], 'correct': 1, 'topic': 'Laws'},
    ],
    'fluid mechanics': [
        {'question': 'What is Reynolds number used to determine?', 'options': ['Heat transfer rate', 'Flow regime (laminar or turbulent)', 'Fluid viscosity', 'Pressure drop'], 'correct': 1, 'topic': 'Flow Regimes'},
        {'question': 'Which equation relates velocity, pressure, and elevation in fluid flow?', 'options': ['Newton\'s equation', 'Bernoulli\'s equation', 'Euler\'s equation', 'Darcy\'s equation'], 'correct': 1, 'topic': 'Fluid Dynamics'},
        {'question': 'What is the continuity equation based on?', 'options': ['Newton\'s second law', 'Conservation of energy', 'Conservation of mass', 'Conservation of momentum'], 'correct': 2, 'topic': 'Fundamentals'},
        {'question': 'What is viscosity?', 'options': ['Resistance to flow', 'Density of fluid', 'Pressure of fluid', 'Temperature of fluid'], 'correct': 0, 'topic': 'Fluid Properties'},
        {'question': 'In laminar flow, Reynolds number is:', 'options': ['> 4000', '2000-4000', '< 2000', '= 1'], 'correct': 2, 'topic': 'Flow Regimes'},
        {'question': 'What is Pascal\'s law?', 'options': ['Pressure in a fluid decreases with depth', 'Pressure applied to fluid is transmitted equally in all directions', 'Fluid flow is inversely proportional to viscosity', 'None'], 'correct': 1, 'topic': 'Hydrostatics'},
        {'question': 'What does the Darcy-Weisbach equation calculate?', 'options': ['Fluid velocity', 'Head loss due to friction in pipes', 'Reynolds number', 'Flow rate'], 'correct': 1, 'topic': 'Pipe Flow'},
        {'question': 'What is buoyancy force equal to?', 'options': ['Mass of object × g', 'Weight of fluid displaced', 'Volume of object × g', 'Density of fluid × g'], 'correct': 1, 'topic': 'Hydrostatics'},
        {'question': 'Which type of flow has parallel streamlines?', 'options': ['Turbulent', 'Laminar', 'Transitional', 'Compressible'], 'correct': 1, 'topic': 'Flow Regimes'},
        {'question': 'What is the unit of dynamic viscosity?', 'options': ['Pa·s', 'm²/s', 'N/m²', 'kg/m³'], 'correct': 0, 'topic': 'Fluid Properties'},
        {'question': 'Bernoulli\'s principle states that as fluid speed increases, pressure:', 'options': ['Increases', 'Decreases', 'Remains constant', 'Doubles'], 'correct': 1, 'topic': 'Fluid Dynamics'},
        {'question': 'What is hydraulic head?', 'options': ['Pressure head + velocity head + elevation head', 'Only pressure head', 'Only velocity head', 'Density × velocity'], 'correct': 0, 'topic': 'Pipe Flow'},
        {'question': 'What is the continuity equation for incompressible flow?', 'options': ['A₁V₁ = A₂V₂', 'P₁V₁ = P₂V₂', 'ρ₁V₁ = ρ₂V₂', 'Q₁ + Q₂ = constant'], 'correct': 0, 'topic': 'Fundamentals'},
        {'question': 'What is a venturimeter used to measure?', 'options': ['Pressure', 'Velocity', 'Flow rate', 'Viscosity'], 'correct': 2, 'topic': 'Flow Measurement'},
        {'question': 'Which law describes pressure variation with depth in a static fluid?', 'options': ['Bernoulli\'s', 'Pascal\'s', 'Hydrostatic law', 'Darcy\'s'], 'correct': 2, 'topic': 'Hydrostatics'},
    ],
    'strength of materials': [
        {'question': 'What is stress?', 'options': ['Force per unit area', 'Force × area', 'Deformation per unit length', 'Force per unit volume'], 'correct': 0, 'topic': 'Basics'},
        {'question': 'What is strain?', 'options': ['Force per unit area', 'Change in length / Original length', 'Stress × Young\'s modulus', 'None'], 'correct': 1, 'topic': 'Basics'},
        {'question': 'What is Young\'s modulus?', 'options': ['Stress / Strain', 'Strain / Stress', 'Stress × Strain', 'None'], 'correct': 0, 'topic': 'Elasticity'},
        {'question': 'What is the unit of stress?', 'options': ['N/m² (Pa)', 'N·m', 'kg/m', 'N·m²'], 'correct': 0, 'topic': 'Basics'},
        {'question': 'Which type of stress occurs when forces act parallel to the cross-section?', 'options': ['Normal stress', 'Shear stress', 'Bending stress', 'Torsional stress'], 'correct': 1, 'topic': 'Types of Stress'},
        {'question': 'What is the neutral axis in a beam?', 'options': ['Axis with maximum stress', 'Axis with zero bending stress', 'Central axis of the beam', 'Axis with maximum shear'], 'correct': 1, 'topic': 'Bending'},
        {'question': 'What does Hooke\'s law state?', 'options': ['Stress is proportional to strain within elastic limit', 'Strain is independent of stress', 'Stress = Strain', 'None'], 'correct': 0, 'topic': 'Elasticity'},
        {'question': 'What is the slenderness ratio used to assess?', 'options': ['Beam deflection', 'Column buckling tendency', 'Shear strength', 'Torsional rigidity'], 'correct': 1, 'topic': 'Columns'},
        {'question': 'What is the formula for Euler\'s critical load for columns?', 'options': ['Pcr = π²EI/L²', 'Pcr = EI/L', 'Pcr = FL/A', 'Pcr = σ×A'], 'correct': 0, 'topic': 'Columns'},
        {'question': 'What is principal stress?', 'options': ['Maximum shear stress', 'Stress on planes where shear stress is zero', 'Average of normal stresses', 'Stress at neutral axis'], 'correct': 1, 'topic': 'Stress Analysis'},
        {'question': 'What is the polar moment of inertia used in?', 'options': ['Bending stress calculation', 'Torsional stress calculation', 'Buckling analysis', 'Shear flow calculation'], 'correct': 1, 'topic': 'Torsion'},
        {'question': 'What is fatigue?', 'options': ['Failure under single large load', 'Failure under repeated cyclic loading', 'Permanent deformation', 'Sudden brittle fracture'], 'correct': 1, 'topic': 'Failure Theories'},
        {'question': 'What is the section modulus?', 'options': ['I/y (moment of inertia / distance from NA)', 'EI', 'GJ', 'AR²'], 'correct': 0, 'topic': 'Bending'},
        {'question': 'Which material property describes resistance to indentation?', 'options': ['Toughness', 'Hardness', 'Ductility', 'Elasticity'], 'correct': 1, 'topic': 'Material Properties'},
        {'question': 'What is Poisson\'s ratio?', 'options': ['Ratio of lateral strain to longitudinal strain', 'Ratio of stress to strain', 'Ratio of shear stress to normal stress', 'None'], 'correct': 0, 'topic': 'Elasticity'},
    ],
    'control systems': [
        {'question': 'What is a transfer function?', 'options': ['Ratio of output to input in Laplace domain', 'Ratio of input to output', 'System time constant', 'Gain of the system'], 'correct': 0, 'topic': 'Basics'},
        {'question': 'What does a closed-loop control system use?', 'options': ['Open loop gain', 'Feedback', 'Feedforward only', 'No sensor'], 'correct': 1, 'topic': 'Control Types'},
        {'question': 'What is the Laplace transform of a unit step function?', 'options': ['1/s', '1/s²', 's', '1'], 'correct': 0, 'topic': 'Laplace Transform'},
        {'question': 'What is steady-state error?', 'options': ['Error at t=0', 'Error as time approaches infinity', 'Maximum overshoot', 'Rise time'], 'correct': 1, 'topic': 'Steady-State Analysis'},
        {'question': 'What does PID stand for?', 'options': ['Proportional-Integral-Derivative', 'Phase-Integral-Delay', 'Pole-Index-Derivative', 'None'], 'correct': 0, 'topic': 'PID Control'},
        {'question': 'A system is stable if all poles are:', 'options': ['On the right half s-plane', 'On the left half s-plane', 'On the imaginary axis', 'At the origin'], 'correct': 1, 'topic': 'Stability'},
        {'question': 'What is the Routh-Hurwitz criterion used for?', 'options': ['Finding poles', 'Stability analysis without finding roots', 'Frequency response', 'Step response'], 'correct': 1, 'topic': 'Stability'},
        {'question': 'What is gain margin?', 'options': ['Phase at 0 dB gain', 'Additional gain before instability', 'System bandwidth', 'Rise time'], 'correct': 1, 'topic': 'Frequency Response'},
        {'question': 'What is phase margin?', 'options': ['Additional phase lag before instability', 'Gain at 0° phase', 'System time constant', 'Settling time'], 'correct': 0, 'topic': 'Frequency Response'},
        {'question': 'What is a Bode plot?', 'options': ['Plot of poles and zeros', 'Gain and phase vs frequency plot', 'Step response plot', 'Root locus plot'], 'correct': 1, 'topic': 'Frequency Response'},
        {'question': 'What does the integral term in PID do?', 'options': ['Reduces rise time', 'Eliminates steady-state error', 'Reduces overshoot', 'Increases damping'], 'correct': 1, 'topic': 'PID Control'},
        {'question': 'What is an open-loop control system?', 'options': ['System with feedback', 'System without feedback', 'Nonlinear system', 'Digital control system'], 'correct': 1, 'topic': 'Control Types'},
        {'question': 'The characteristic equation of a control system is obtained from:', 'options': ['Numerator of closed-loop TF', 'Denominator of closed-loop TF', 'Open-loop gain', 'Step response'], 'correct': 1, 'topic': 'Basics'},
        {'question': 'What is the root locus technique used for?', 'options': ['Analyzing frequency response', 'Designing controllers by plotting poles vs gain', 'Measuring step response', 'Finding transfer functions'], 'correct': 1, 'topic': 'Root Locus'},
        {'question': 'What is a first-order system characterized by?', 'options': ['One pole, no zeros', 'Two poles', 'One zero', 'Complex conjugate poles'], 'correct': 0, 'topic': 'System Types'},
    ],
    'robotics': [
        {'question': 'What does DOF stand for in robotics?', 'options': ['Direction of Force', 'Degrees of Freedom', 'Design of Function', 'Density of Fluid'], 'correct': 1, 'topic': 'Fundamentals'},
        {'question': 'What is forward kinematics?', 'options': ['Finding end-effector position from joint angles', 'Finding joint angles from end-effector position', 'Planning robot path', 'Calculating forces'], 'correct': 0, 'topic': 'Kinematics'},
        {'question': 'What is inverse kinematics?', 'options': ['Finding end-effector from joint angles', 'Finding joint angles from desired end-effector position', 'Calculating robot speed', 'Path planning'], 'correct': 1, 'topic': 'Kinematics'},
        {'question': 'What is ROS?', 'options': ['Robot Operating System', 'Robotic Output Sensor', 'Remote Operation Software', 'Robotic Object Scanner'], 'correct': 0, 'topic': 'ROS'},
        {'question': 'What is a ROS topic?', 'options': ['A service call', 'A message-passing channel between nodes', 'A launch file', 'A robot model'], 'correct': 1, 'topic': 'ROS'},
        {'question': 'What is SLAM?', 'options': ['Simultaneous Localization and Mapping', 'Sequential Linear Algebra Method', 'Software Library for Autonomous Machines', 'None'], 'correct': 0, 'topic': 'Navigation'},
        {'question': 'What is a PID controller used for in robotics?', 'options': ['Path planning', 'Closed-loop motion control', 'Sensor fusion', 'Computer vision'], 'correct': 1, 'topic': 'Control'},
        {'question': 'Which algorithm is commonly used for robot path planning?', 'options': ['Bubble sort', 'A* algorithm', 'Quick sort', 'Binary search'], 'correct': 1, 'topic': 'Path Planning'},
        {'question': 'What is a Kalman filter used for?', 'options': ['Image processing', 'State estimation and sensor fusion', 'Path planning', 'Motor control'], 'correct': 1, 'topic': 'Sensors'},
        {'question': 'What is a LiDAR sensor?', 'options': ['Camera for RGB images', 'Light detection and ranging sensor for 3D point clouds', 'Sound-based sensor', 'GPS module'], 'correct': 1, 'topic': 'Sensors'},
        {'question': 'What is end-effector in a robotic arm?', 'options': ['First joint', 'Base link', 'The tool at the end of the arm', 'Motor controller'], 'correct': 2, 'topic': 'Fundamentals'},
        {'question': 'What is a holonomic robot?', 'options': ['Robot that can move in any direction without turning', 'Robot with only one wheel', 'Flying robot', 'Underwater robot'], 'correct': 0, 'topic': 'Mobile Robots'},
        {'question': 'What is odometry?', 'options': ['Measuring temperature', 'Estimating robot position using wheel encoders', 'Measuring current', 'Sensor fusion technique'], 'correct': 1, 'topic': 'Navigation'},
        {'question': 'What is Gazebo?', 'options': ['A path planning algorithm', 'A 3D robot simulation environment', 'A robot operating system', 'A sensor type'], 'correct': 1, 'topic': 'ROS'},
        {'question': 'What is the DH (Denavit-Hartenberg) convention?', 'options': ['A path planning method', 'A standard method for describing robot kinematics', 'A sensor fusion algorithm', 'A control method'], 'correct': 1, 'topic': 'Kinematics'},
    ],
    'engineering mathematics': [
        {'question': 'What is the Laplace transform of e^(at)?', 'options': ['1/(s-a)', '1/(s+a)', 's/(s-a)', 'a/(s-a)'], 'correct': 0, 'topic': 'Laplace Transform'},
        {'question': 'What is the rank of a matrix?', 'options': ['Number of rows', 'Number of non-zero rows in row echelon form', 'Number of columns', 'Determinant value'], 'correct': 1, 'topic': 'Linear Algebra'},
        {'question': 'What is a differential equation?', 'options': ['Equation with derivatives', 'Algebraic equation', 'Trigonometric equation', 'Matrix equation'], 'correct': 0, 'topic': 'Differential Equations'},
        {'question': 'What is the Fourier series used for?', 'options': ['Representing periodic functions as sum of sinusoids', 'Solving differential equations only', 'Matrix multiplication', 'Integration'], 'correct': 0, 'topic': 'Fourier Analysis'},
        {'question': 'What is the eigenvalue of a matrix?', 'options': ['A scalar λ where Av = λv', 'The determinant', 'The trace', 'A row in the matrix'], 'correct': 0, 'topic': 'Linear Algebra'},
        {'question': 'What is the gradient of a scalar field?', 'options': ['A scalar', 'A vector pointing in direction of steepest ascent', 'A matrix', 'A differential equation'], 'correct': 1, 'topic': 'Vector Calculus'},
        {'question': 'What is the divergence theorem?', 'options': ['Relates surface integral to volume integral', 'Relates line integral to area integral', 'Solves differential equations', 'None'], 'correct': 0, 'topic': 'Vector Calculus'},
        {'question': 'What is the Z-transform used for?', 'options': ['Continuous-time systems', 'Discrete-time systems', 'Analog circuits', 'Matrix operations'], 'correct': 1, 'topic': 'Transforms'},
        {'question': 'What is the order of a differential equation?', 'options': ['Degree of highest power', 'Order of highest derivative', 'Number of variables', 'None'], 'correct': 1, 'topic': 'Differential Equations'},
        {'question': 'What does det(A) = 0 mean for matrix A?', 'options': ['A is invertible', 'A is singular (not invertible)', 'A has all zero rows', 'A is diagonal'], 'correct': 1, 'topic': 'Linear Algebra'},
        {'question': 'What is the curl of a vector field?', 'options': ['A measure of rotation/circulation', 'A measure of divergence', 'A scalar field', 'None'], 'correct': 0, 'topic': 'Vector Calculus'},
        {'question': 'What is the convolution theorem in Fourier analysis?', 'options': ['Convolution in time = multiplication in frequency', 'Multiplication in time = multiplication in frequency', 'Integration in time = differentiation in frequency', 'None'], 'correct': 0, 'topic': 'Fourier Analysis'},
        {'question': 'What is the numerical method used to solve ODEs step by step?', 'options': ['Gauss elimination', 'Runge-Kutta method', 'LU decomposition', 'Newton-Raphson'], 'correct': 1, 'topic': 'Numerical Methods'},
        {'question': 'What is a Hermitian matrix?', 'options': ['A matrix equal to its complex conjugate transpose', 'A symmetric matrix', 'A diagonal matrix', 'An identity matrix'], 'correct': 0, 'topic': 'Linear Algebra'},
        {'question': 'What does the Laplacian operator ∇² represent?', 'options': ['Sum of second partial derivatives', 'Gradient of gradient', 'Divergence of gradient', 'All of the above'], 'correct': 3, 'topic': 'Vector Calculus'},
    ],
    'digital electronics': [
        {'question': 'What is the output of an AND gate when inputs are 1 and 0?', 'options': ['1', '0', 'Undefined', 'Depends on voltage'], 'correct': 1, 'topic': 'Logic Gates'},
        {'question': 'What is the universal gate?', 'options': ['AND', 'OR', 'NAND', 'XOR'], 'correct': 2, 'topic': 'Logic Gates'},
        {'question': 'How many bits are in one byte?', 'options': ['4', '8', '16', '32'], 'correct': 1, 'topic': 'Number Systems'},
        {'question': 'What is a flip-flop?', 'options': ['Combinational circuit', 'Sequential circuit that stores one bit', 'Counter', 'Decoder'], 'correct': 1, 'topic': 'Sequential Logic'},
        {'question': 'What is the 2\'s complement of 0101 (4-bit)?', 'options': ['1011', '1010', '1110', '0110'], 'correct': 0, 'topic': 'Number Systems'},
        {'question': 'What is a multiplexer?', 'options': ['Selects one of many inputs based on select lines', 'Decodes binary to decimal', 'Converts digital to analog', 'Stores data'], 'correct': 0, 'topic': 'Combinational Logic'},
        {'question': 'What is the output of XOR gate when both inputs are 1?', 'options': ['1', '0', 'Undefined', 'High impedance'], 'correct': 1, 'topic': 'Logic Gates'},
        {'question': 'What is a D flip-flop?', 'options': ['Data flip-flop that stores input D on clock edge', 'Delay circuit', 'Down counter', 'Differential amplifier'], 'correct': 0, 'topic': 'Sequential Logic'},
        {'question': 'What is the hexadecimal equivalent of decimal 255?', 'options': ['EF', 'FF', 'FE', 'EE'], 'correct': 1, 'topic': 'Number Systems'},
        {'question': 'What is a decoder?', 'options': ['n inputs to 2^n outputs', '2^n inputs to n outputs', 'Selects one of many inputs', 'Stores binary data'], 'correct': 0, 'topic': 'Combinational Logic'},
        {'question': 'What is a state machine?', 'options': ['A combinational circuit', 'A sequential circuit with defined states and transitions', 'A memory element', 'A counter'], 'correct': 1, 'topic': 'Sequential Logic'},
        {'question': 'What is the Boolean expression for NAND gate?', 'options': ['A·B', '~(A·B)', 'A+B', '~(A+B)'], 'correct': 1, 'topic': 'Logic Gates'},
        {'question': 'What is an encoder?', 'options': ['2^n inputs to n outputs', 'n inputs to 2^n outputs', 'Memory device', 'Adder circuit'], 'correct': 0, 'topic': 'Combinational Logic'},
        {'question': 'What type of memory loses data when power is off?', 'options': ['ROM', 'Flash memory', 'RAM', 'EEPROM'], 'correct': 2, 'topic': 'Memory'},
        {'question': 'What is Karnaugh map (K-map) used for?', 'options': ['Arithmetic operations', 'Simplifying Boolean expressions', 'Sequential circuit design', 'Encoding'], 'correct': 1, 'topic': 'Combinational Logic'},
    ],
    'cybersecurity fundamentals': [
        {'question': 'What does CIA stand for in cybersecurity?', 'options': ['Central Intelligence Agency', 'Confidentiality, Integrity, Availability', 'Code, Integrity, Authentication', 'None'], 'correct': 1, 'topic': 'Fundamentals'},
        {'question': 'What is a firewall?', 'options': ['Hardware device only', 'Network security barrier that monitors traffic', 'A type of virus', 'An encryption algorithm'], 'correct': 1, 'topic': 'Network Security'},
        {'question': 'What is phishing?', 'options': ['Scanning for open ports', 'Fraudulent attempt to obtain sensitive information', 'DDoS attack', 'Malware injection'], 'correct': 1, 'topic': 'Social Engineering'},
        {'question': 'What is encryption?', 'options': ['Deleting data', 'Converting data to an unreadable format', 'Compressing data', 'Backing up data'], 'correct': 1, 'topic': 'Cryptography'},
        {'question': 'What is a VPN?', 'options': ['Virtual Private Network', 'Virtual Public Network', 'Verified Protocol Network', 'None'], 'correct': 0, 'topic': 'Network Security'},
        {'question': 'What is SQL injection?', 'options': ['Inserting SQL code to manipulate a database', 'A database command', 'A networking protocol', 'Encrypting database'], 'correct': 0, 'topic': 'Web Security'},
        {'question': 'What is two-factor authentication?', 'options': ['Two passwords', 'Two steps of identity verification', 'Double encryption', 'None'], 'correct': 1, 'topic': 'Authentication'},
        {'question': 'What is a DDoS attack?', 'options': ['Data Deletion and Override', 'Distributed Denial of Service', 'Dynamic Data Output System', 'None'], 'correct': 1, 'topic': 'Attacks'},
        {'question': 'What is malware?', 'options': ['Bad hardware', 'Malicious software', 'A network protocol', 'Encryption method'], 'correct': 1, 'topic': 'Malware'},
        {'question': 'What does HTTPS provide over HTTP?', 'options': ['Faster speed', 'Encryption and secure communication', 'More features', 'Larger data transfer'], 'correct': 1, 'topic': 'Web Security'},
    ],
    'cloud computing': [
        {'question': 'What does SaaS stand for?', 'options': ['Software as a Service', 'System as a Service', 'Storage as a Service', 'Server as a Service'], 'correct': 0, 'topic': 'Cloud Models'},
        {'question': 'Which cloud model provides virtual machines?', 'options': ['SaaS', 'PaaS', 'IaaS', 'FaaS'], 'correct': 2, 'topic': 'Cloud Models'},
        {'question': 'What is auto-scaling?', 'options': ['Manual scaling of resources', 'Automatically adjusting resources based on demand', 'Scaling the database', 'Increasing storage only'], 'correct': 1, 'topic': 'Scalability'},
        {'question': 'What is a container?', 'options': ['A physical server', 'Lightweight portable software unit', 'A virtual machine', 'A cloud storage bucket'], 'correct': 1, 'topic': 'Containers'},
        {'question': 'What is Kubernetes?', 'options': ['A programming language', 'Container orchestration system', 'Cloud storage service', 'CI/CD tool'], 'correct': 1, 'topic': 'Containers'},
        {'question': 'What is serverless computing?', 'options': ['Computing without any servers', 'Running code without managing servers', 'Offline computing', 'None'], 'correct': 1, 'topic': 'Serverless'},
        {'question': 'What is the benefit of cloud computing?', 'options': ['Higher hardware costs', 'On-demand scalability and cost savings', 'Less security', 'Fixed resources'], 'correct': 1, 'topic': 'Benefits'},
        {'question': 'What is CI/CD?', 'options': ['Computer Integration/Computer Delivery', 'Continuous Integration/Continuous Delivery', 'Code Inspection/Code Deployment', 'None'], 'correct': 1, 'topic': 'DevOps'},
        {'question': 'What is AWS?', 'options': ['A programming language', 'Amazon Web Services — a cloud platform', 'An OS', 'A database'], 'correct': 1, 'topic': 'Cloud Providers'},
        {'question': 'What is a load balancer?', 'options': ['A server that balances load electrically', 'Distributes network traffic across multiple servers', 'A storage device', 'A database tool'], 'correct': 1, 'topic': 'Architecture'},
        {'question': 'What is Infrastructure as Code (IaC)?', 'options': ['Writing code to manage infrastructure', 'A cloud provider', 'A container technology', 'A database model'], 'correct': 0, 'topic': 'DevOps'},
        {'question': 'What is a CDN?', 'options': ['Content Delivery Network', 'Central Data Node', 'Cloud Data Network', 'None'], 'correct': 0, 'topic': 'Architecture'},
    ],
    'ui/ux fundamentals': [
        {'question': 'What is UX design primarily focused on?', 'options': ['Visual aesthetics only', 'Overall user experience and usability', 'Coding the interface', 'Marketing'], 'correct': 1, 'topic': 'UX Basics'},
        {'question': 'What is a wireframe?', 'options': ['Final visual design', 'Low-fidelity layout sketch of a UI', 'A code framework', 'A hardware blueprint'], 'correct': 1, 'topic': 'Design Process'},
        {'question': 'What is a user persona?', 'options': ['An avatar in a game', 'A fictional representation of a target user', 'A UI component', 'A design pattern'], 'correct': 1, 'topic': 'User Research'},
        {'question': 'What does usability testing involve?', 'options': ['Testing code performance', 'Observing real users interacting with a design', 'Only checking visual design', 'None'], 'correct': 1, 'topic': 'Testing'},
        {'question': 'What is the first step in the design thinking process?', 'options': ['Prototype', 'Ideate', 'Empathize', 'Test'], 'correct': 2, 'topic': 'Design Thinking'},
        {'question': 'What is visual hierarchy in UI design?', 'options': ['Using only one color', 'Arranging elements to guide user attention', 'Making all elements equal size', 'None'], 'correct': 1, 'topic': 'Visual Design'},
        {'question': 'What does Figma primarily support?', 'options': ['Video editing', 'Collaborative UI/UX design and prototyping', 'Code compilation', 'Database management'], 'correct': 1, 'topic': 'Tools'},
        {'question': 'What is a prototype?', 'options': ['Final product', 'A working simulation of a design', 'A backend service', 'A color palette'], 'correct': 1, 'topic': 'Design Process'},
        {'question': 'What is the purpose of a design system?', 'options': ['To write code', 'To provide consistent reusable UI components and guidelines', 'To create wireframes', 'To conduct user research'], 'correct': 1, 'topic': 'Design Systems'},
        {'question': 'What does WCAG stand for?', 'options': ['Web Content Accessibility Guidelines', 'Web Code and Graphics', 'Website Creation And Guidelines', 'None'], 'correct': 0, 'topic': 'Accessibility'},
    ],
}



class TestAIService:
    """Service for generating test questions and evaluating tests."""
    
    def __init__(self):
        self.ai = AIService()
    
    def generate_questions(self, skill, difficulty, num_questions):
        """
        Generate test questions.
        Uses AI if available, falls back to question bank.
        """
        if self.ai.is_available:
            ai_questions = self._generate_ai_questions(skill, difficulty, num_questions)
            if ai_questions:
                return ai_questions
        
        return self._get_bank_questions(skill, difficulty, num_questions)
    
    def _generate_ai_questions(self, skill, difficulty, num_questions):
        """Generate questions using OpenAI."""
        prompt = f"""Generate {num_questions} multiple-choice questions for a {difficulty} level {skill} assessment.

Requirements:
- Each question has 4 options
- Only one correct answer
- Include a topic for each question
- Questions should test {difficulty} level knowledge of {skill}

Respond as a JSON array with this structure:
[
  {{
    "question": "Question text?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct": 0,
    "topic": "Topic Name"
  }}
]

The "correct" field is the index (0-3) of the correct option."""

        messages = [
            {"role": "system", "content": "You are an expert assessment creator. Generate MCQ questions and respond with valid JSON only."},
            {"role": "user", "content": prompt}
        ]
        
        result = self.ai.chat_completion_json(messages, temperature=0.7, max_tokens=2000)
        if isinstance(result, list) and len(result) > 0:
            # Validate structure
            valid = []
            for q in result:
                if all(k in q for k in ['question', 'options', 'correct', 'topic']):
                    if isinstance(q['options'], list) and len(q['options']) == 4:
                        valid.append(q)
            if valid:
                return valid[:num_questions]
        return None
    
    def _get_bank_questions(self, skill, difficulty, num_questions):
        """Get questions from the question bank with smart domain matching."""
        skill_key = skill.lower().strip()
        bank = TEST_BANKS.get(skill_key, [])
        
        if not bank:
            # Try partial/fuzzy matching for multi-word or variant names
            for key in TEST_BANKS:
                if key in skill_key or skill_key in key:
                    bank = TEST_BANKS[key]
                    break
        
        if not bank:
            # Try word-level matching (e.g. "Strength of Materials" → 'strength of materials')
            skill_words = set(skill_key.split())
            best_key = None
            best_overlap = 0
            for key in TEST_BANKS:
                key_words = set(key.split())
                overlap = len(skill_words & key_words)
                if overlap > best_overlap:
                    best_overlap = overlap
                    best_key = key
            if best_key and best_overlap >= 1:
                bank = TEST_BANKS[best_key]
        
        if not bank:
            # Generic fallback — use data structures (more neutral than Python)
            bank = TEST_BANKS.get('data structures', TEST_BANKS.get('python', []))

        
        # Shuffle and select
        selected = random.sample(bank, min(num_questions, len(bank)))
        
        # If we need more, cycle through
        while len(selected) < num_questions and bank:
            remaining = num_questions - len(selected)
            pool = [q for q in bank if q not in selected]
            if pool:
                selected.extend(random.sample(pool, min(remaining, len(pool))))
            else:
                break
        
        return selected[:num_questions]
    
    def evaluate_test(self, questions, user_answers, time_taken):
        """
        Evaluate a completed test.
        questions: list of question dicts
        user_answers: dict of question_index -> selected_option_index
        time_taken: seconds
        """
        total = len(questions)
        correct = 0
        wrong = 0
        results = []
        topic_stats = {}
        
        for i, question in enumerate(questions):
            user_answer = user_answers.get(str(i), -1)
            correct_answer = question['correct']
            topic = question.get('topic', 'General')
            is_correct = user_answer == correct_answer
            
            if is_correct:
                correct += 1
            else:
                wrong += 1
            
            # Track topic performance
            if topic not in topic_stats:
                topic_stats[topic] = {'correct': 0, 'total': 0}
            topic_stats[topic]['total'] += 1
            if is_correct:
                topic_stats[topic]['correct'] += 1
            
            results.append({
                'question': question['question'],
                'options': question['options'],
                'selected_answer': user_answer,
                'correct_answer': correct_answer,
                'is_correct': is_correct,
                'topic': topic,
            })
        
        score = int((correct / total) * 100) if total > 0 else 0
        accuracy = score
        
        # Calculate topic performance
        topic_performance = {}
        for topic, stats in topic_stats.items():
            topic_performance[topic] = {
                'correct': stats['correct'],
                'total': stats['total'],
                'accuracy': int((stats['correct'] / stats['total']) * 100),
            }
        
        # Identify strong and weak topics
        strong_topics = sorted(
            [(t, p['accuracy']) for t, p in topic_performance.items() if p['accuracy'] >= 70],
            key=lambda x: x[1], reverse=True
        )
        weak_topics = sorted(
            [(t, p['accuracy']) for t, p in topic_performance.items() if p['accuracy'] < 70],
            key=lambda x: x[1]
        )
        
        # Generate suggestions
        suggestions = self._generate_suggestions(strong_topics, weak_topics)
        
        return {
            'score': score,
            'accuracy': accuracy,
            'correct': correct,
            'wrong': wrong,
            'total': total,
            'time_taken': time_taken,
            'results': results,
            'topic_performance': topic_performance,
            'strong_topics': strong_topics,
            'weak_topics': weak_topics,
            'suggestions': suggestions,
        }
    
    def _generate_suggestions(self, strong_topics, weak_topics):
        """Generate improvement suggestions."""
        suggestions = []
        
        for topic, accuracy in weak_topics[:3]:
            suggestions.append(f"Your performance in {topic} is {accuracy}%. Focus on reviewing the core concepts and practicing more problems.")
        
        if strong_topics:
            top_strong = strong_topics[0]
            suggestions.append(f"Excellent work in {top_strong[0]} with {top_strong[1]}% accuracy. Keep it up!")
        
        if not weak_topics:
            suggestions.append("Outstanding performance across all topics! Consider taking a more advanced assessment.")
        
        if not suggestions:
            suggestions.append("Continue practicing to improve your overall performance.")
        
        return suggestions
