"""
Roadmap AI service - generates personalized learning roadmaps.
"""
import json
import random
from .openai_service import AIService



# Predefined roadmap templates by career
ROADMAP_TEMPLATES = {
    'cad': [
        {'phase': 'CAD & Drafting Fundamentals', 'skills': ['AutoCAD', '2D Drafting', 'Engineering Graphics'], 'topics': ['Sketching', 'Dimensions', 'Layers', 'Orthographic projections', 'GD&T basics'], 'goals': 'Master 2D drafting and technical drawing principles', 'project': 'Create 2D mechanical assembly drawings in AutoCAD', 'duration': '3-4 weeks', 'difficulty': 'Beginner'},
        {'phase': '3D Part Modeling', 'skills': ['SolidWorks', 'CATIA', '3D Modeling', 'Parametric Design'], 'topics': ['Extrude', 'Revolve', 'Fillet', 'Feature tree', 'Parent-child relations'], 'goals': 'Build complex 3D solid parts from sketches', 'project': 'Model a multi-featured mechanical component', 'duration': '4-5 weeks', 'difficulty': 'Beginner'},
        {'phase': 'Assembly Design & Mates', 'skills': ['SolidWorks Assembly', 'Interference Check', 'BOM'], 'topics': ['Standard mates', 'Mechanical mates', 'Top-down design', 'Bill of Materials'], 'goals': 'Assemble multi-part systems with proper constraints', 'project': 'Design an engine or gearbox assembly with BOM', 'duration': '4-5 weeks', 'difficulty': 'Intermediate'},
        {'phase': 'Surface Modeling & Sheet Metal', 'skills': ['Surfacing', 'Sheet Metal Design', 'Weldments'], 'topics': ['Loft', 'Sweep', 'K-factor', 'Bend allowance', 'Structural members'], 'goals': 'Master complex organic shapes and sheet metal parts', 'project': 'Design a consumer product casing with sheet metal and surfacing', 'duration': '4-6 weeks', 'difficulty': 'Intermediate'},
        {'phase': 'Simulation & DFM', 'skills': ['CAD FEA', 'Stress Analysis', 'DFM/DFA'], 'topics': ['Static stress', 'Factor of safety', 'Draft angles', 'Injection molding rules'], 'goals': 'Validate structural integrity and design for manufacturing', 'project': 'Perform FEA stress analysis on a CAD bracket model', 'duration': '4-5 weeks', 'difficulty': 'Advanced'},
        {'phase': 'Projects & Portfolio', 'skills': ['Photorealistic Rendering', 'KeyShot', 'Portfolio'], 'topics': ['Materials', 'Lighting', 'Exploded views', 'Technical documentation'], 'goals': 'Create a professional CAD design portfolio', 'project': 'Complete 2-3 detailed CAD model projects with renders', 'duration': '4-6 weeks', 'difficulty': 'Advanced'},
    ],
    'data scientist': [
        {'phase': 'Python Foundations', 'skills': ['Python basics', 'Data structures', 'OOP', 'File handling'], 'topics': ['Variables', 'Loops', 'Functions', 'Lists', 'Dictionaries'], 'goals': 'Master Python programming fundamentals', 'project': 'Build a CLI-based data processing tool', 'duration': '2-3 weeks', 'difficulty': 'Beginner'},
        {'phase': 'Data Analysis', 'skills': ['Pandas', 'NumPy', 'Matplotlib', 'Seaborn'], 'topics': ['DataFrames', 'Data cleaning', 'Visualization', 'Statistical analysis'], 'goals': 'Learn to manipulate and visualize data', 'project': 'Analyze a real dataset and create visualizations', 'duration': '3-4 weeks', 'difficulty': 'Beginner'},
        {'phase': 'SQL & Databases', 'skills': ['SQL', 'PostgreSQL', 'Database design'], 'topics': ['Queries', 'Joins', 'Aggregations', 'Normalization'], 'goals': 'Master database querying and design', 'project': 'Design and query a database for a real-world scenario', 'duration': '2-3 weeks', 'difficulty': 'Intermediate'},
        {'phase': 'Statistics & Math', 'skills': ['Statistics', 'Probability', 'Linear algebra'], 'topics': ['Distributions', 'Hypothesis testing', 'Regression', 'Matrices'], 'goals': 'Build statistical foundation for ML', 'project': 'Statistical analysis of a dataset with hypothesis testing', 'duration': '3-4 weeks', 'difficulty': 'Intermediate'},
        {'phase': 'Machine Learning', 'skills': ['Scikit-learn', 'Regression', 'Classification', 'Clustering'], 'topics': ['Supervised learning', 'Unsupervised learning', 'Model evaluation', 'Cross-validation'], 'goals': 'Learn core ML algorithms', 'project': 'Build a predictive model end-to-end', 'duration': '4-6 weeks', 'difficulty': 'Advanced'},
        {'phase': 'Deep Learning', 'skills': ['TensorFlow', 'PyTorch', 'Neural networks'], 'topics': ['CNNs', 'RNNs', 'Transfer learning', 'Model optimization'], 'goals': 'Understand deep learning architectures', 'project': 'Build an image classifier or text model', 'duration': '4-6 weeks', 'difficulty': 'Advanced'},
        {'phase': 'Projects & Portfolio', 'skills': ['Git', 'Deployment', 'Documentation'], 'topics': ['Version control', 'Model deployment', 'Portfolio building'], 'goals': 'Build a portfolio of projects', 'project': 'Complete 2-3 end-to-end ML projects', 'duration': '4-8 weeks', 'difficulty': 'Advanced'},
        {'phase': 'Interview Preparation', 'skills': ['ML system design', 'Coding interviews', 'Behavioral'], 'topics': ['ML fundamentals', 'Coding problems', 'Case studies'], 'goals': 'Prepare for data science interviews', 'project': 'Mock interviews and coding practice', 'duration': '2-4 weeks', 'difficulty': 'Intermediate'},
    ],
    'data analyst': [
        {'phase': 'Excel & Basics', 'skills': ['Excel', 'Google Sheets', 'Data basics'], 'topics': ['Formulas', 'Pivot tables', 'Charts', 'Data cleaning'], 'goals': 'Master spreadsheet analysis', 'project': 'Create a comprehensive Excel dashboard', 'duration': '2 weeks', 'difficulty': 'Beginner'},
        {'phase': 'SQL Fundamentals', 'skills': ['SQL', 'MySQL', 'PostgreSQL'], 'topics': ['SELECT', 'JOIN', 'GROUP BY', 'Subqueries'], 'goals': 'Query databases effectively', 'project': 'Build queries for a sample e-commerce database', 'duration': '3 weeks', 'difficulty': 'Beginner'},
        {'phase': 'Python for Data', 'skills': ['Python', 'Pandas', 'NumPy'], 'topics': ['DataFrames', 'Data manipulation', 'Cleaning', 'Analysis'], 'goals': 'Analyze data with Python', 'project': 'Data analysis pipeline for a real dataset', 'duration': '3-4 weeks', 'difficulty': 'Intermediate'},
        {'phase': 'Data Visualization', 'skills': ['Tableau', 'Power BI', 'Matplotlib'], 'topics': ['Dashboards', 'Storytelling', 'Interactive viz', 'Design principles'], 'goals': 'Create compelling visualizations', 'project': 'Build an interactive dashboard', 'duration': '3 weeks', 'difficulty': 'Intermediate'},
        {'phase': 'Statistics', 'skills': ['Statistics', 'A/B testing', 'Probability'], 'topics': ['Descriptive stats', 'Inferential stats', 'Hypothesis testing', 'Distributions'], 'goals': 'Apply statistics to business problems', 'project': 'A/B test analysis for a product feature', 'duration': '3 weeks', 'difficulty': 'Intermediate'},
        {'phase': 'Advanced Analysis', 'skills': ['Python', 'SQL', 'ETL'], 'topics': ['Data pipelines', 'Automation', 'Reporting', 'Forecasting basics'], 'goals': 'Build automated analysis workflows', 'project': 'Automated reporting dashboard', 'duration': '4 weeks', 'difficulty': 'Advanced'},
        {'phase': 'Projects & Portfolio', 'skills': ['Git', 'Documentation', 'Presentation'], 'topics': ['Project documentation', 'Portfolio building', 'Storytelling'], 'goals': 'Build analyst portfolio', 'project': 'Complete 3 analysis projects with dashboards', 'duration': '4-6 weeks', 'difficulty': 'Intermediate'},
        {'phase': 'Interview Preparation', 'skills': ['SQL interviews', 'Case studies', 'Behavioral'], 'topics': ['SQL problems', 'Analytics cases', 'Communication'], 'goals': 'Ace analyst interviews', 'project': 'Practice SQL and case interview problems', 'duration': '2-3 weeks', 'difficulty': 'Intermediate'},
    ],
    'software engineer': [
        {'phase': 'Programming Basics', 'skills': ['Python or Java', 'C', 'Problem solving'], 'topics': ['Variables', 'Loops', 'Functions', 'Arrays', 'Strings'], 'goals': 'Build strong programming fundamentals', 'project': 'Build a console-based application', 'duration': '3-4 weeks', 'difficulty': 'Beginner'},
        {'phase': 'Data Structures', 'skills': ['Arrays', 'Linked Lists', 'Trees', 'Stacks', 'Queues'], 'topics': ['Linear structures', 'Trees', 'Hash tables', 'Graphs'], 'goals': 'Master core data structures', 'project': 'Implement data structures from scratch', 'duration': '4-6 weeks', 'difficulty': 'Intermediate'},
        {'phase': 'Algorithms', 'skills': ['Sorting', 'Searching', 'Dynamic programming', 'Greedy'], 'topics': ['Time complexity', 'Sorting algorithms', 'Graph algorithms', 'DP'], 'goals': 'Solve algorithmic problems efficiently', 'project': 'Solve 50+ problems on LeetCode/HackerRank', 'duration': '6-8 weeks', 'difficulty': 'Advanced'},
        {'phase': 'Databases', 'skills': ['SQL', 'Database design', 'ORM'], 'topics': ['Normalization', 'Queries', 'Indexes', 'Transactions'], 'goals': 'Design and query databases', 'project': 'Design a database for a web application', 'duration': '3-4 weeks', 'difficulty': 'Intermediate'},
        {'phase': 'Web Development', 'skills': ['HTML', 'CSS', 'JavaScript', 'Framework'], 'topics': ['Frontend basics', 'Backend APIs', 'REST', 'Authentication'], 'goals': 'Build web applications', 'project': 'Build a full-stack web app', 'duration': '6-8 weeks', 'difficulty': 'Intermediate'},
        {'phase': 'System Design', 'skills': ['Architecture', 'Scalability', 'Design patterns'], 'topics': ['Design patterns', 'Scalability', 'Load balancing', 'Caching'], 'goals': 'Design scalable systems', 'project': 'Design a system like URL shortener or chat app', 'duration': '4-6 weeks', 'difficulty': 'Advanced'},
        {'phase': 'Projects & Portfolio', 'skills': ['Git', 'CI/CD', 'Deployment'], 'topics': ['Version control', 'Testing', 'Deployment', 'Documentation'], 'goals': 'Build a strong portfolio', 'project': 'Deploy 2-3 projects with tests', 'duration': '4-8 weeks', 'difficulty': 'Intermediate'},
        {'phase': 'Interview Preparation', 'skills': ['DSA', 'System design', 'Behavioral'], 'topics': ['Coding rounds', 'System design', 'HR rounds'], 'goals': 'Crack SDE interviews', 'project': 'Mock interviews and problem practice', 'duration': '4-6 weeks', 'difficulty': 'Advanced'},
    ],
    'full stack developer': [
        {'phase': 'HTML, CSS & JavaScript', 'skills': ['HTML5', 'CSS3', 'JavaScript ES6+'], 'topics': ['Semantic HTML', 'Flexbox/Grid', 'DOM', 'Async JS'], 'goals': 'Master frontend fundamentals', 'project': 'Build a responsive landing page', 'duration': '3-4 weeks', 'difficulty': 'Beginner'},
        {'phase': 'Frontend Framework', 'skills': ['React', 'Vue or Angular', 'TypeScript'], 'topics': ['Components', 'State management', 'Routing', 'Hooks'], 'goals': 'Build dynamic frontend apps', 'project': 'Build a SPA with routing and state', 'duration': '4-6 weeks', 'difficulty': 'Intermediate'},
        {'phase': 'Backend Development', 'skills': ['Node.js', 'Python/Django', 'REST APIs'], 'topics': ['Server basics', 'API design', 'Authentication', 'Middleware'], 'goals': 'Build backend APIs', 'project': 'Build a REST API with auth', 'duration': '4-6 weeks', 'difficulty': 'Intermediate'},
        {'phase': 'Database & ORM', 'skills': ['SQL', 'PostgreSQL', 'MongoDB', 'Prisma/ORM'], 'topics': ['Schema design', 'Queries', 'Relations', 'Migrations'], 'goals': 'Manage data effectively', 'project': 'Database integration with backend', 'duration': '3-4 weeks', 'difficulty': 'Intermediate'},
        {'phase': 'Authentication & Security', 'skills': ['JWT', 'OAuth', 'Security best practices'], 'topics': ['Auth flows', 'Security headers', 'Input validation', 'CORS'], 'goals': 'Secure your applications', 'project': 'Add auth to your full-stack app', 'duration': '2-3 weeks', 'difficulty': 'Advanced'},
        {'phase': 'DevOps & Deployment', 'skills': ['Docker', 'CI/CD', 'Cloud', 'Nginx'], 'topics': ['Containerization', 'Pipelines', 'Cloud deployment', 'Monitoring'], 'goals': 'Deploy and manage apps', 'project': 'Deploy your app with CI/CD', 'duration': '4 weeks', 'difficulty': 'Advanced'},
        {'phase': 'Projects & Portfolio', 'skills': ['Git', 'Documentation', 'Testing'], 'topics': ['Project structure', 'Testing', 'Documentation', 'Portfolio'], 'goals': 'Build impressive projects', 'project': 'Complete 2-3 full-stack projects', 'duration': '6-8 weeks', 'difficulty': 'Intermediate'},
        {'phase': 'Interview Preparation', 'skills': ['DSA', 'System design', 'Frontend/Backend'], 'topics': ['Coding rounds', 'System design', 'Framework deep dives'], 'goals': 'Crack full-stack interviews', 'project': 'Mock interviews and portfolio review', 'duration': '3-4 weeks', 'difficulty': 'Advanced'},
    ],
    'machine learning engineer': [
        {'phase': 'Python & Math', 'skills': ['Python', 'Linear algebra', 'Calculus', 'Statistics'], 'topics': ['NumPy', 'Matrices', 'Derivatives', 'Probability'], 'goals': 'Build ML math foundation', 'project': 'Implement linear regression from scratch', 'duration': '4-6 weeks', 'difficulty': 'Intermediate'},
        {'phase': 'Classical ML', 'skills': ['Scikit-learn', 'Regression', 'Classification', 'Clustering'], 'topics': ['Supervised', 'Unsupervised', 'Ensemble', 'Evaluation'], 'goals': 'Master classical algorithms', 'project': 'Kaggle competition entry', 'duration': '4-6 weeks', 'difficulty': 'Intermediate'},
        {'phase': 'Deep Learning', 'skills': ['TensorFlow', 'PyTorch', 'Neural networks'], 'topics': ['MLP', 'CNN', 'RNN', 'Optimization'], 'goals': 'Build deep learning models', 'project': 'Image classification with CNNs', 'duration': '6-8 weeks', 'difficulty': 'Advanced'},
        {'phase': 'NLP & Computer Vision', 'skills': ['Transformers', 'NLP', 'CV', 'Transfer learning'], 'topics': ['Tokenization', 'Embeddings', 'Attention', 'Fine-tuning'], 'goals': 'Specialize in NLP or CV', 'project': 'Fine-tune a pre-trained model', 'duration': '6-8 weeks', 'difficulty': 'Advanced'},
        {'phase': 'MLOps & Deployment', 'skills': ['Docker', 'MLflow', 'Model serving', 'Monitoring'], 'topics': ['Model packaging', 'APIs', 'A/B testing', 'Monitoring'], 'goals': 'Deploy ML models', 'project': 'Deploy a model as an API', 'duration': '4 weeks', 'difficulty': 'Advanced'},
        {'phase': 'Projects & Portfolio', 'skills': ['Git', 'Documentation', 'Research'], 'topics': ['End-to-end projects', 'Documentation', 'Reproducibility'], 'goals': 'Build ML portfolio', 'project': '2-3 end-to-end ML projects', 'duration': '6-10 weeks', 'difficulty': 'Advanced'},
        {'phase': 'Interview Preparation', 'skills': ['ML fundamentals', 'Coding', 'ML system design'], 'topics': ['ML theory', 'Coding rounds', 'ML design'], 'goals': 'Crack ML interviews', 'project': 'Mock ML interviews', 'duration': '3-4 weeks', 'difficulty': 'Advanced'},
    ],
    'devops engineer': [
        {'phase': 'Linux & Scripting', 'skills': ['Linux', 'Bash', 'Python scripting'], 'topics': ['Commands', 'Shell scripting', 'File system', 'Processes'], 'goals': 'Master Linux administration', 'project': 'Automate system tasks with scripts', 'duration': '3-4 weeks', 'difficulty': 'Beginner'},
        {'phase': 'Version Control & CI/CD', 'skills': ['Git', 'GitHub Actions', 'Jenkins'], 'topics': ['Branching', 'Merging', 'Pipelines', 'Automation'], 'goals': 'Automate build and deployment', 'project': 'Set up CI/CD pipeline', 'duration': '3-4 weeks', 'difficulty': 'Intermediate'},
        {'phase': 'Containers & Orchestration', 'skills': ['Docker', 'Kubernetes', 'Helm'], 'topics': ['Containerization', 'Pods', 'Services', 'Deployments'], 'goals': 'Master container orchestration', 'project': 'Deploy a multi-container app', 'duration': '6-8 weeks', 'difficulty': 'Advanced'},
        {'phase': 'Cloud Platforms', 'skills': ['AWS', 'Azure or GCP', 'Terraform'], 'topics': ['Compute', 'Storage', 'Networking', 'IaC'], 'goals': 'Manage cloud infrastructure', 'project': 'Provision infrastructure with Terraform', 'duration': '6-8 weeks', 'difficulty': 'Advanced'},
        {'phase': 'Monitoring & Logging', 'skills': ['Prometheus', 'Grafana', 'ELK stack'], 'topics': ['Metrics', 'Alerts', 'Log aggregation', 'Dashboards'], 'goals': 'Set up observability', 'project': 'Complete monitoring stack', 'duration': '3-4 weeks', 'difficulty': 'Intermediate'},
        {'phase': 'Security & Best Practices', 'skills': ['Security', 'Compliance', 'Secrets management'], 'topics': ['DevSecOps', 'Vulnerability scanning', 'Secret management', 'Policies'], 'goals': 'Secure the pipeline', 'project': 'Security audit and remediation', 'duration': '3 weeks', 'difficulty': 'Advanced'},
        {'phase': 'Projects & Portfolio', 'skills': ['Documentation', 'Automation', 'GitOps'], 'topics': ['End-to-end automation', 'Documentation', 'Portfolio'], 'goals': 'Build DevOps portfolio', 'project': 'Complete DevOps pipeline project', 'duration': '4-6 weeks', 'difficulty': 'Advanced'},
        {'phase': 'Interview Preparation', 'skills': ['Linux', 'Kubernetes', 'System design'], 'topics': ['Troubleshooting', 'Architecture', 'Scenarios'], 'goals': 'Crack DevOps interviews', 'project': 'Mock interviews and scenario practice', 'duration': '2-3 weeks', 'difficulty': 'Intermediate'},
    ],
    'mechanical engineer': [
        {'phase': 'Engineering Fundamentals', 'skills': ['Engineering Mathematics', 'Physics', 'Engineering Drawing'], 'topics': ['Calculus', 'Differential equations', 'Mechanics', 'AutoCAD basics'], 'goals': 'Build strong engineering foundations', 'project': 'Create engineering drawings using AutoCAD', 'duration': '4-6 weeks', 'difficulty': 'Beginner'},
        {'phase': 'Core Mechanical Subjects', 'skills': ['Thermodynamics', 'Fluid Mechanics', 'Solid Mechanics'], 'topics': ['Laws of thermodynamics', 'Heat transfer', 'Fluid flow', 'Stress & strain'], 'goals': 'Master core mechanical principles', 'project': 'Thermal system analysis project', 'duration': '6-8 weeks', 'difficulty': 'Intermediate'},
        {'phase': 'Design & Manufacturing', 'skills': ['CAD (SolidWorks/CATIA)', 'Manufacturing processes', 'Machine Design'], 'topics': ['3D modeling', 'CNC machining', 'Gear design', 'Tolerances'], 'goals': 'Learn design tools and manufacturing', 'project': 'Design a mechanical component in SolidWorks', 'duration': '6-8 weeks', 'difficulty': 'Intermediate'},
        {'phase': 'Simulation & Analysis', 'skills': ['FEA (ANSYS)', 'CFD basics', 'MATLAB'], 'topics': ['Finite element analysis', 'Stress simulation', 'MATLAB programming'], 'goals': 'Perform engineering simulations', 'project': 'Structural analysis of a component using ANSYS', 'duration': '4-6 weeks', 'difficulty': 'Advanced'},
        {'phase': 'Automation & Mechatronics', 'skills': ['PLC programming', 'Mechatronics', 'Industrial automation'], 'topics': ['PLC ladder logic', 'Sensors & actuators', 'SCADA', 'Robotics basics'], 'goals': 'Understand industrial automation and mechatronics', 'project': 'Build an automated conveyor system simulation', 'duration': '4-6 weeks', 'difficulty': 'Advanced'},
        {'phase': 'Industry Tools & Quality', 'skills': ['SAP ERP', 'Six Sigma', 'ISO standards', 'Project management'], 'topics': ['ERP systems', 'DMAIC', 'QC tools', 'Lean manufacturing'], 'goals': 'Learn industry tools and quality standards', 'project': 'Quality improvement project using Six Sigma tools', 'duration': '3-4 weeks', 'difficulty': 'Intermediate'},
        {'phase': 'Projects & Portfolio', 'skills': ['Technical report writing', 'Research', 'Documentation'], 'topics': ['Project planning', 'Research methodology', 'Portfolio building'], 'goals': 'Build a strong engineering portfolio', 'project': 'Complete 2-3 end-to-end mechanical engineering projects', 'duration': '4-6 weeks', 'difficulty': 'Intermediate'},
        {'phase': 'Interview Preparation', 'skills': ['Core subjects review', 'Aptitude', 'Technical interviews'], 'topics': ['Thermodynamics', 'Fluid mechanics', 'Machine design', 'Manufacturing processes'], 'goals': 'Crack mechanical engineering interviews', 'project': 'Mock interviews and GATE/PSU aptitude practice', 'duration': '3-4 weeks', 'difficulty': 'Intermediate'},
    ],
    'mechanical engineering': [
        {'phase': 'Engineering Fundamentals', 'skills': ['Engineering Mathematics', 'Physics', 'Engineering Drawing'], 'topics': ['Calculus', 'Differential equations', 'Mechanics', 'AutoCAD basics'], 'goals': 'Build strong engineering foundations', 'project': 'Create engineering drawings using AutoCAD', 'duration': '4-6 weeks', 'difficulty': 'Beginner'},
        {'phase': 'Core Mechanical Subjects', 'skills': ['Thermodynamics', 'Fluid Mechanics', 'Solid Mechanics'], 'topics': ['Laws of thermodynamics', 'Heat transfer', 'Fluid flow', 'Stress & strain'], 'goals': 'Master core mechanical principles', 'project': 'Thermal system analysis project', 'duration': '6-8 weeks', 'difficulty': 'Intermediate'},
        {'phase': 'Design & Manufacturing', 'skills': ['CAD (SolidWorks/CATIA)', 'Manufacturing processes', 'Machine Design'], 'topics': ['3D modeling', 'CNC machining', 'Gear design', 'GD&T'], 'goals': 'Learn design tools and manufacturing', 'project': 'Design a mechanical component in SolidWorks', 'duration': '6-8 weeks', 'difficulty': 'Intermediate'},
        {'phase': 'Simulation & Analysis', 'skills': ['FEA (ANSYS)', 'CFD basics', 'MATLAB'], 'topics': ['Finite element analysis', 'Stress simulation', 'MATLAB programming'], 'goals': 'Perform engineering simulations', 'project': 'Structural analysis of a component using ANSYS', 'duration': '4-6 weeks', 'difficulty': 'Advanced'},
        {'phase': 'Automation & Mechatronics', 'skills': ['PLC programming', 'Mechatronics', 'Industrial automation'], 'topics': ['PLC ladder logic', 'Sensors & actuators', 'SCADA', 'Robotics basics'], 'goals': 'Understand industrial automation', 'project': 'Build an automated system simulation', 'duration': '4-6 weeks', 'difficulty': 'Advanced'},
        {'phase': 'Industry Tools & Quality', 'skills': ['SAP ERP', 'Six Sigma', 'ISO standards'], 'topics': ['ERP systems', 'DMAIC', 'QC tools', 'Lean manufacturing'], 'goals': 'Learn industry tools and quality standards', 'project': 'Quality improvement project using Six Sigma', 'duration': '3-4 weeks', 'difficulty': 'Intermediate'},
        {'phase': 'Projects & Portfolio', 'skills': ['Technical report writing', 'Research', 'Documentation'], 'topics': ['Project planning', 'Research methodology', 'Portfolio building'], 'goals': 'Build a strong engineering portfolio', 'project': 'Complete 2-3 end-to-end mechanical projects', 'duration': '4-6 weeks', 'difficulty': 'Intermediate'},
        {'phase': 'Interview Preparation', 'skills': ['Core subjects review', 'Aptitude', 'Technical interviews'], 'topics': ['Thermodynamics', 'Fluid mechanics', 'Machine design', 'Manufacturing'], 'goals': 'Crack mechanical engineering interviews', 'project': 'Mock interviews and aptitude practice', 'duration': '3-4 weeks', 'difficulty': 'Intermediate'},
    ],
    'robotics engineer': [
        {'phase': 'Robotics Foundations', 'skills': ['Mathematics', 'Physics', 'Python/C++ basics'], 'topics': ['Linear algebra', 'Kinematics', 'Dynamics', 'Control theory basics'], 'goals': 'Build mathematical and programming foundation for robotics', 'project': 'Simulate a 2D robot arm in Python', 'duration': '4-6 weeks', 'difficulty': 'Beginner'},
        {'phase': 'Robot Kinematics & Dynamics', 'skills': ['Forward/Inverse Kinematics', 'Jacobians', 'Dynamics modeling'], 'topics': ['DH parameters', 'Workspace analysis', 'Euler angles', 'Trajectory planning'], 'goals': 'Understand robot motion and control', 'project': 'Implement forward kinematics for a 3-DOF robot', 'duration': '4-6 weeks', 'difficulty': 'Intermediate'},
        {'phase': 'ROS (Robot Operating System)', 'skills': ['ROS/ROS2', 'Linux', 'C++ & Python in ROS'], 'topics': ['Nodes', 'Topics', 'Services', 'Launch files', 'Gazebo simulation'], 'goals': 'Master the ROS ecosystem', 'project': 'Build a mobile robot simulation in Gazebo', 'duration': '5-7 weeks', 'difficulty': 'Intermediate'},
        {'phase': 'Sensors & Perception', 'skills': ['LiDAR', 'Camera/OpenCV', 'IMU', 'Sensor fusion'], 'topics': ['Point clouds', 'Computer vision basics', 'Kalman filter', 'SLAM'], 'goals': 'Process sensor data for robot perception', 'project': 'Implement obstacle detection with LiDAR', 'duration': '4-6 weeks', 'difficulty': 'Advanced'},
        {'phase': 'Path Planning & Navigation', 'skills': ['Path planning algorithms', 'SLAM', 'Navigation stack'], 'topics': ['A* algorithm', 'RRT', 'SLAM techniques', 'ROS Nav stack'], 'goals': 'Enable autonomous robot navigation', 'project': 'Autonomous navigation in a simulated environment', 'duration': '4-6 weeks', 'difficulty': 'Advanced'},
        {'phase': 'Robot Control & Embedded Systems', 'skills': ['PID control', 'State machines', 'Arduino/Raspberry Pi'], 'topics': ['PID tuning', 'Motor control', 'Embedded programming', 'Real-time systems'], 'goals': 'Control physical robot hardware', 'project': 'Build and control a line-following robot', 'duration': '4-5 weeks', 'difficulty': 'Advanced'},
        {'phase': 'AI & Machine Learning for Robotics', 'skills': ['Deep learning', 'Reinforcement learning', 'Computer vision'], 'topics': ['CNN for object detection', 'RL for robot control', 'Sim-to-real transfer'], 'goals': 'Apply AI to robotics problems', 'project': 'Object detection and grasping with a robot arm', 'duration': '5-7 weeks', 'difficulty': 'Advanced'},
        {'phase': 'Projects & Interview Preparation', 'skills': ['Robotics system design', 'Documentation', 'Communication'], 'topics': ['End-to-end robot projects', 'Research papers', 'Interview preparation'], 'goals': 'Build robotics portfolio and prepare for jobs', 'project': 'Build an end-to-end autonomous robot project', 'duration': '4-6 weeks', 'difficulty': 'Advanced'},
    ],
    'robotics': [
        {'phase': 'Robotics Foundations', 'skills': ['Mathematics', 'Physics', 'Python/C++ basics'], 'topics': ['Linear algebra', 'Kinematics', 'Dynamics', 'Control theory basics'], 'goals': 'Build mathematical and programming foundation', 'project': 'Simulate a robot arm in Python', 'duration': '4-6 weeks', 'difficulty': 'Beginner'},
        {'phase': 'Robot Kinematics & Dynamics', 'skills': ['Forward/Inverse Kinematics', 'Jacobians', 'Trajectory planning'], 'topics': ['DH parameters', 'Workspace analysis', 'Euler angles', 'Velocity kinematics'], 'goals': 'Understand robot motion thoroughly', 'project': 'Kinematics solver for a robotic arm', 'duration': '4-6 weeks', 'difficulty': 'Intermediate'},
        {'phase': 'ROS (Robot Operating System)', 'skills': ['ROS/ROS2', 'Linux', 'Python/C++ in ROS'], 'topics': ['Nodes', 'Topics', 'Services', 'Gazebo simulation'], 'goals': 'Master the ROS ecosystem', 'project': 'Build a mobile robot in Gazebo with ROS', 'duration': '5-7 weeks', 'difficulty': 'Intermediate'},
        {'phase': 'Sensors, Vision & Perception', 'skills': ['LiDAR', 'OpenCV', 'IMU', 'Sensor fusion'], 'topics': ['Point clouds', 'Object detection', 'Kalman filter', 'SLAM'], 'goals': 'Process sensor data for robot perception', 'project': 'Real-time obstacle detection system', 'duration': '4-6 weeks', 'difficulty': 'Advanced'},
        {'phase': 'Navigation & Path Planning', 'skills': ['Path planning', 'SLAM', 'ROS Nav stack'], 'topics': ['A*, RRT, Dijkstra', 'SLAM techniques', 'Costmaps', 'Global/local planners'], 'goals': 'Implement autonomous navigation', 'project': 'Autonomous navigation for a simulated robot', 'duration': '4-6 weeks', 'difficulty': 'Advanced'},
        {'phase': 'Robot Control Systems', 'skills': ['PID control', 'State machines', 'Embedded systems'], 'topics': ['PID tuning', 'Motor control', 'Real-time programming'], 'goals': 'Control physical robot hardware', 'project': 'Build a PID-controlled robot', 'duration': '4-5 weeks', 'difficulty': 'Advanced'},
        {'phase': 'AI for Robotics', 'skills': ['Reinforcement learning', 'Deep learning', 'Computer vision'], 'topics': ['DQN', 'Policy gradient', 'Object detection', 'Sim-to-real'], 'goals': 'Apply AI/ML to robotics', 'project': 'Train a robot to navigate using RL', 'duration': '5-7 weeks', 'difficulty': 'Advanced'},
        {'phase': 'Projects & Interview Preparation', 'skills': ['System design', 'Research', 'Communication'], 'topics': ['End-to-end robotics project', 'Research papers', 'Mock interviews'], 'goals': 'Build robotics portfolio', 'project': 'Complete a full autonomous robotics project', 'duration': '4-6 weeks', 'difficulty': 'Advanced'},
    ],
    'civil engineer': [
        {'phase': 'Engineering Fundamentals', 'skills': ['Engineering Mathematics', 'Engineering Drawing', 'Surveying'], 'topics': ['Calculus', 'Matrices', 'AutoCAD', 'Leveling and traversing'], 'goals': 'Build civil engineering foundations', 'project': 'Create site plan using AutoCAD', 'duration': '4-5 weeks', 'difficulty': 'Beginner'},
        {'phase': 'Structural Engineering', 'skills': ['Strength of Materials', 'Structural Analysis', 'RCC Design'], 'topics': ['Beams', 'Columns', 'Trusses', 'RCC design codes (IS 456)'], 'goals': 'Understand structural behavior and design', 'project': 'Design a simply supported RCC beam', 'duration': '6-8 weeks', 'difficulty': 'Intermediate'},
        {'phase': 'Geotechnical Engineering', 'skills': ['Soil Mechanics', 'Foundation Design', 'Rock Mechanics'], 'topics': ['Soil classification', 'Bearing capacity', 'Settlement analysis', 'Foundation types'], 'goals': 'Understand soil behavior and foundation design', 'project': 'Foundation design for a sample building', 'duration': '4-5 weeks', 'difficulty': 'Intermediate'},
        {'phase': 'Hydraulics & Water Resources', 'skills': ['Fluid Mechanics', 'Hydrology', 'Irrigation Engineering'], 'topics': ['Flow in pipes', 'Open channel flow', 'Watershed management', 'Dam design'], 'goals': 'Design hydraulic structures and water systems', 'project': 'Drainage design for a residential area', 'duration': '4-5 weeks', 'difficulty': 'Intermediate'},
        {'phase': 'Transportation & Environment', 'skills': ['Highway Engineering', 'Traffic Engineering', 'Environmental Engineering'], 'topics': ['Pavement design', 'Traffic flow theory', 'Water treatment', 'Waste management'], 'goals': 'Design transportation and environmental systems', 'project': 'Highway alignment and pavement design', 'duration': '4-5 weeks', 'difficulty': 'Intermediate'},
        {'phase': 'Construction Management', 'skills': ['Project Management', 'Cost estimation', 'Construction methods'], 'topics': ['CPM/PERT scheduling', 'BOQ preparation', 'Contract management', 'Safety norms'], 'goals': 'Manage construction projects effectively', 'project': 'Project schedule and cost estimate for a building', 'duration': '3-4 weeks', 'difficulty': 'Intermediate'},
        {'phase': 'Civil Engineering Software', 'skills': ['AutoCAD', 'STAAD Pro', 'ETABS', 'Revit/BIM'], 'topics': ['Structural modeling', 'Analysis and design', 'BIM workflows'], 'goals': 'Use industry-standard civil engineering software', 'project': 'Model and analyze a structure in STAAD Pro', 'duration': '4-5 weeks', 'difficulty': 'Advanced'},
        {'phase': 'Interview Preparation', 'skills': ['Core subjects review', 'GATE preparation', 'Technical interviews'], 'topics': ['SOM', 'Fluid mechanics', 'Geotechnical', 'Structural analysis'], 'goals': 'Crack civil engineering interviews and exams', 'project': 'GATE preparation and mock tests', 'duration': '4-6 weeks', 'difficulty': 'Intermediate'},
    ],
    'electrical engineer': [
        {'phase': 'Electrical Fundamentals', 'skills': ['Circuit Theory', 'Engineering Mathematics', 'Basic Electronics'], 'topics': ['KVL, KCL', 'Mesh analysis', 'Thevenin theorem', 'Diodes, transistors'], 'goals': 'Master electrical circuit fundamentals', 'project': 'Simulate basic circuits in LTSpice', 'duration': '4-5 weeks', 'difficulty': 'Beginner'},
        {'phase': 'Electromagnetic Theory', 'skills': ['Electromagnetic Fields', 'Transmission Lines', 'Antennas'], 'topics': ["Maxwell's equations", 'Wave propagation', 'TL parameters', 'Antenna radiation'], 'goals': 'Understand electromagnetic principles', 'project': 'Field simulation using available EM tools', 'duration': '4-5 weeks', 'difficulty': 'Intermediate'},
        {'phase': 'Power Systems & Machines', 'skills': ['Power Systems', 'Power Electronics', 'Electrical Machines'], 'topics': ['Transformers', 'Induction motors', 'Inverters', 'Grid stability'], 'goals': 'Design and analyze power systems', 'project': 'Power flow analysis using MATLAB/PSCAD', 'duration': '5-7 weeks', 'difficulty': 'Intermediate'},
        {'phase': 'Control Systems', 'skills': ['Control Systems', 'MATLAB/Simulink', 'Digital Control'], 'topics': ['Transfer functions', 'Bode plots', 'PID control', 'State space'], 'goals': 'Design and analyze control systems', 'project': 'PID controller design for a DC motor in MATLAB', 'duration': '4-5 weeks', 'difficulty': 'Intermediate'},
        {'phase': 'Digital Electronics & Embedded Systems', 'skills': ['Digital Electronics', 'Microcontrollers (Arduino/STM32)', 'VHDL/Verilog'], 'topics': ['Logic gates', 'Flip-flops', 'FPGA programming', 'Embedded C'], 'goals': 'Design digital and embedded systems', 'project': 'Build an embedded system project with a microcontroller', 'duration': '5-6 weeks', 'difficulty': 'Advanced'},
        {'phase': 'Signal Processing', 'skills': ['Signals & Systems', 'DSP', 'MATLAB'], 'topics': ['Fourier transform', 'FIR/IIR Filters', 'Z-transform', 'Digital signal processing'], 'goals': 'Process and analyze electrical signals', 'project': 'Design a digital filter for audio processing', 'duration': '4-5 weeks', 'difficulty': 'Advanced'},
        {'phase': 'Projects & Portfolio', 'skills': ['PCB Design (KiCad)', 'Documentation', 'Research'], 'topics': ['PCB layout', 'Schematic design', 'Project documentation'], 'goals': 'Build electrical engineering portfolio', 'project': 'Design and fabricate a PCB project', 'duration': '4-6 weeks', 'difficulty': 'Advanced'},
        {'phase': 'Interview Preparation', 'skills': ['Core subjects review', 'GATE preparation', 'Technical interviews'], 'topics': ['Circuit theory', 'Power systems', 'Control systems', 'EMT'], 'goals': 'Crack electrical engineering interviews', 'project': 'GATE preparation and company-specific prep', 'duration': '3-4 weeks', 'difficulty': 'Intermediate'},
    ],
    'aerospace engineer': [
        {'phase': 'Aerospace Fundamentals', 'skills': ['Engineering Mathematics', 'Physics', 'Engineering Drawing'], 'topics': ['Vector calculus', 'Differential equations', 'Mechanics', '2D/3D drawing'], 'goals': 'Build strong aerospace foundations', 'project': 'Aerodynamic shape design sketch', 'duration': '4-5 weeks', 'difficulty': 'Beginner'},
        {'phase': 'Aerodynamics', 'skills': ['Fluid Mechanics', 'Aerodynamics', 'CFD basics'], 'topics': ['Lift and drag', 'Airfoil theory', 'Boundary layers', 'Compressible flow'], 'goals': 'Understand aerodynamic principles', 'project': 'CFD analysis of an airfoil using OpenFOAM', 'duration': '5-7 weeks', 'difficulty': 'Intermediate'},
        {'phase': 'Flight Mechanics & Structures', 'skills': ['Flight mechanics', 'Aircraft structures', 'Composite materials'], 'topics': ['Equations of motion', 'Stability and control', 'Structural loads', 'FEA'], 'goals': 'Analyze aircraft flight and structural behavior', 'project': 'Flight stability analysis of a simple aircraft model', 'duration': '5-6 weeks', 'difficulty': 'Intermediate'},
        {'phase': 'Propulsion Systems', 'skills': ['Thermodynamics', 'Gas dynamics', 'Propulsion'], 'topics': ['Jet engines', 'Rocket propulsion', 'Nozzle design', 'Combustion'], 'goals': 'Understand aircraft and spacecraft propulsion', 'project': 'Turbojet engine thermodynamic cycle analysis', 'duration': '4-5 weeks', 'difficulty': 'Intermediate'},
        {'phase': 'Avionics & Flight Control', 'skills': ['Control systems', 'Navigation systems', 'Avionics'], 'topics': ['Autopilot systems', 'GPS/INS integration', 'Flight management systems', 'PID control'], 'goals': 'Design aircraft control and navigation systems', 'project': 'Autopilot simulation in MATLAB/Simulink', 'duration': '4-5 weeks', 'difficulty': 'Advanced'},
        {'phase': 'Space Systems', 'skills': ['Orbital mechanics', 'Spacecraft design', 'Remote sensing'], 'topics': ["Kepler's laws", 'Orbital maneuvers', 'Satellite design', 'Launch vehicles'], 'goals': 'Understand space systems engineering', 'project': 'Orbital transfer simulation', 'duration': '4-5 weeks', 'difficulty': 'Advanced'},
        {'phase': 'Projects & Portfolio', 'skills': ['CATIA/SolidWorks', 'Research writing', 'Simulation tools'], 'topics': ['Aircraft design project', 'Technical paper writing', 'Portfolio building'], 'goals': 'Build an aerospace engineering portfolio', 'project': 'Complete an aircraft or UAV design project', 'duration': '5-7 weeks', 'difficulty': 'Advanced'},
        {'phase': 'Interview Preparation', 'skills': ['Core subjects review', 'GATE/ISRO/DRDO prep', 'Technical interviews'], 'topics': ['Aerodynamics', 'Flight mechanics', 'Propulsion', 'Structures'], 'goals': 'Crack aerospace engineering interviews', 'project': 'Mock interviews and exam preparation', 'duration': '3-4 weeks', 'difficulty': 'Intermediate'},
    ],
    'ui/ux designer': [
        {'phase': 'Design Fundamentals', 'skills': ['Design principles', 'Color theory', 'Typography'], 'topics': ['Visual hierarchy', 'Gestalt principles', 'Color psychology', 'Font pairing'], 'goals': 'Build a strong visual design foundation', 'project': 'Redesign a webpage with improved visual hierarchy', 'duration': '2-3 weeks', 'difficulty': 'Beginner'},
        {'phase': 'UX Research & Strategy', 'skills': ['User research', 'Personas', 'User journey mapping'], 'topics': ['User interviews', 'Surveys', 'Empathy mapping', 'User flows'], 'goals': 'Understand users and define UX strategy', 'project': 'Conduct user research for an app concept', 'duration': '3-4 weeks', 'difficulty': 'Beginner'},
        {'phase': 'Wireframing & Prototyping', 'skills': ['Figma', 'Adobe XD', 'Wireframing', 'Prototyping'], 'topics': ['Low-fi wireframes', 'Hi-fi mockups', 'Interactive prototypes', 'Component libraries'], 'goals': 'Create wireframes and interactive prototypes', 'project': 'Design a complete app prototype in Figma', 'duration': '4-5 weeks', 'difficulty': 'Intermediate'},
        {'phase': 'Usability & Testing', 'skills': ['Usability testing', 'A/B testing', 'Heuristic evaluation'], 'topics': ["Nielsen's heuristics", 'User testing sessions', 'Accessibility (WCAG)', 'Iterating on feedback'], 'goals': 'Test and improve design usability', 'project': 'Run usability tests and iterate on your prototype', 'duration': '3-4 weeks', 'difficulty': 'Intermediate'},
        {'phase': 'Design Systems', 'skills': ['Design systems', 'Component libraries', 'Documentation'], 'topics': ['Atomic design', 'Design tokens', 'Consistency standards', 'Handoff to developers'], 'goals': 'Build scalable design systems', 'project': 'Create a design system for a brand', 'duration': '3-4 weeks', 'difficulty': 'Advanced'},
        {'phase': 'Interaction Design & Motion', 'skills': ['Micro-interactions', 'Animation', 'Motion design'], 'topics': ['Animation principles', 'Transitions', 'Loading states', 'Feedback loops'], 'goals': 'Design delightful interactions', 'project': 'Add micro-interactions to your app prototype', 'duration': '3-4 weeks', 'difficulty': 'Advanced'},
        {'phase': 'Portfolio & Case Studies', 'skills': ['Portfolio building', 'Case studies', 'Storytelling'], 'topics': ['Writing case studies', 'Behance/Dribbble', 'Portfolio website', 'Design thinking'], 'goals': 'Build a standout UX portfolio', 'project': 'Complete 3 case studies for portfolio', 'duration': '4-6 weeks', 'difficulty': 'Intermediate'},
        {'phase': 'Interview Preparation', 'skills': ['Design critique', 'Whiteboard challenges', 'Behavioral'], 'topics': ['Portfolio presentation', 'Design decisions rationale', 'Stakeholder communication'], 'goals': 'Ace UX/UI design interviews', 'project': 'Mock design challenges and portfolio review', 'duration': '2-3 weeks', 'difficulty': 'Intermediate'},
    ],
    'cybersecurity engineer': [
        {'phase': 'Networking Fundamentals', 'skills': ['Networking', 'TCP/IP', 'DNS/HTTP/HTTPS'], 'topics': ['OSI model', 'Protocols', 'Subnetting', 'Firewalls'], 'goals': 'Master networking fundamentals for security', 'project': 'Set up a small network and analyze traffic with Wireshark', 'duration': '3-4 weeks', 'difficulty': 'Beginner'},
        {'phase': 'Linux & Security Basics', 'skills': ['Linux', 'Bash scripting', 'Security concepts'], 'topics': ['Linux commands', 'File permissions', 'Encryption basics', 'CIA triad'], 'goals': 'Learn Linux and basic security concepts', 'project': 'Harden a Linux server configuration', 'duration': '3-4 weeks', 'difficulty': 'Beginner'},
        {'phase': 'Ethical Hacking & Pentesting', 'skills': ['Kali Linux', 'Nmap', 'Metasploit', 'Burp Suite'], 'topics': ['Reconnaissance', 'Vulnerability scanning', 'Exploitation', 'Web app testing'], 'goals': 'Perform ethical hacking and penetration testing', 'project': 'Pentest a vulnerable VM (HackTheBox/TryHackMe)', 'duration': '5-7 weeks', 'difficulty': 'Intermediate'},
        {'phase': 'Web Application Security', 'skills': ['OWASP Top 10', 'SQL injection', 'XSS', 'CSRF'], 'topics': ['Injection attacks', 'Authentication flaws', 'Security misconfigurations', 'Broken access control'], 'goals': 'Identify and fix web application vulnerabilities', 'project': 'Attack and defend a vulnerable web app (DVWA)', 'duration': '4-5 weeks', 'difficulty': 'Intermediate'},
        {'phase': 'Cryptography & PKI', 'skills': ['Cryptography', 'SSL/TLS', 'PKI', 'Hashing'], 'topics': ['Symmetric/Asymmetric encryption', 'RSA', 'AES', 'Digital certificates'], 'goals': 'Understand cryptographic systems', 'project': 'Implement and test encryption/decryption programs', 'duration': '3-4 weeks', 'difficulty': 'Intermediate'},
        {'phase': 'Incident Response & SIEM', 'skills': ['SIEM (Splunk/ELK)', 'Log analysis', 'Digital forensics', 'Threat hunting'], 'topics': ['Log analysis', 'Incident handling', 'Memory forensics', 'Threat intelligence'], 'goals': 'Respond to and investigate security incidents', 'project': 'Analyze a mock incident using Splunk', 'duration': '4-5 weeks', 'difficulty': 'Advanced'},
        {'phase': 'Certifications & CTF', 'skills': ['CompTIA Security+', 'CEH', 'OSCP preparation'], 'topics': ['Certification preparation', 'CTF challenges', 'Security reports writing'], 'goals': 'Get certified and build cybersecurity portfolio', 'project': 'Complete CTF challenges and prepare for certifications', 'duration': '5-8 weeks', 'difficulty': 'Advanced'},
        {'phase': 'Interview Preparation', 'skills': ['Security concepts', 'Scenario-based questions', 'Behavioral'], 'topics': ['Security fundamentals', 'Incident response scenarios', 'Common vulnerabilities'], 'goals': 'Crack cybersecurity interviews', 'project': 'Mock cybersecurity interviews', 'duration': '2-3 weeks', 'difficulty': 'Intermediate'},
    ],
    'cloud engineer': [
        {'phase': 'Cloud Fundamentals', 'skills': ['Cloud concepts', 'Virtualization', 'Linux basics'], 'topics': ['IaaS/PaaS/SaaS', 'Cloud providers overview', 'Virtualization concepts', 'Linux commands'], 'goals': 'Understand cloud computing fundamentals', 'project': 'Deploy a virtual machine on AWS/Azure/GCP free tier', 'duration': '2-3 weeks', 'difficulty': 'Beginner'},
        {'phase': 'AWS/Azure/GCP Core Services', 'skills': ['Compute (EC2)', 'Storage (S3)', 'Networking (VPC)', 'Databases (RDS)'], 'topics': ['EC2 instances', 'S3 buckets', 'VPC setup', 'Load balancers', 'Security groups'], 'goals': 'Use core cloud services confidently', 'project': 'Host a web application on AWS with S3, EC2, and RDS', 'duration': '5-6 weeks', 'difficulty': 'Intermediate'},
        {'phase': 'Infrastructure as Code', 'skills': ['Terraform', 'CloudFormation', 'Ansible'], 'topics': ['IaC concepts', 'Terraform state management', 'Resource provisioning', 'Modules and workspaces'], 'goals': 'Automate cloud infrastructure provisioning', 'project': 'Provision a 3-tier architecture with Terraform', 'duration': '4-5 weeks', 'difficulty': 'Intermediate'},
        {'phase': 'Containers & Kubernetes', 'skills': ['Docker', 'Kubernetes', 'Helm', 'EKS/AKS/GKE'], 'topics': ['Containerization', 'Pods', 'Services', 'Deployments', 'Managed Kubernetes'], 'goals': 'Deploy containerized applications at scale', 'project': 'Deploy a microservices app on Kubernetes', 'duration': '5-6 weeks', 'difficulty': 'Advanced'},
        {'phase': 'CI/CD & GitOps', 'skills': ['GitHub Actions', 'Jenkins', 'ArgoCD'], 'topics': ['Pipeline design', 'Automated testing', 'GitOps principles', 'Deployment strategies (blue-green, canary)'], 'goals': 'Build automated deployment pipelines', 'project': 'Build a full CI/CD pipeline from code to production', 'duration': '3-4 weeks', 'difficulty': 'Advanced'},
        {'phase': 'Cloud Security & Monitoring', 'skills': ['IAM', 'CloudWatch', 'Prometheus/Grafana', 'Security best practices'], 'topics': ['Least privilege', 'Encryption', 'Alerts', 'Dashboards', 'Cost optimization'], 'goals': 'Secure and monitor cloud environments', 'project': 'Set up monitoring and alerting for a cloud app', 'duration': '3-4 weeks', 'difficulty': 'Advanced'},
        {'phase': 'Certifications & Architecture', 'skills': ['AWS Solutions Architect', 'CKA', 'Azure Administrator'], 'topics': ['Certification prep', 'Cloud architecture patterns', 'Well-Architected Framework'], 'goals': 'Get cloud certified and design scalable architectures', 'project': 'Document and present a cloud architecture design', 'duration': '5-8 weeks', 'difficulty': 'Advanced'},
        {'phase': 'Interview Preparation', 'skills': ['Cloud concepts', 'Architecture design', 'Troubleshooting'], 'topics': ['System design on cloud', 'Cost optimization', 'HA/DR strategies'], 'goals': 'Crack cloud engineering interviews', 'project': 'Mock cloud architecture interviews', 'duration': '2-3 weeks', 'difficulty': 'Intermediate'},
    ],
    'product manager': [
        {'phase': 'Product Management Fundamentals', 'skills': ['Product thinking', 'Market research', 'Customer empathy'], 'topics': ['Product lifecycle', 'Market sizing', 'User needs', 'Value proposition canvas'], 'goals': 'Understand the product management role', 'project': 'Write a Product Requirements Document (PRD)', 'duration': '2-3 weeks', 'difficulty': 'Beginner'},
        {'phase': 'User Research & Data Analysis', 'skills': ['User interviews', 'Surveys', 'Data analysis', 'SQL basics'], 'topics': ['Qualitative research', 'Quantitative analysis', 'NPS', 'Customer journey mapping'], 'goals': 'Conduct user research and derive insights', 'project': 'Conduct user interviews and synthesize insights', 'duration': '3-4 weeks', 'difficulty': 'Beginner'},
        {'phase': 'Product Strategy & Roadmapping', 'skills': ['Product strategy', 'OKRs', 'Prioritization frameworks'], 'topics': ['Vision & mission', 'OKR framework', 'RICE/MoSCoW prioritization', 'Roadmapping tools'], 'goals': 'Define product strategy and roadmap', 'project': 'Create a 6-month product roadmap', 'duration': '3-4 weeks', 'difficulty': 'Intermediate'},
        {'phase': 'Agile & Product Execution', 'skills': ['Agile/Scrum', 'JIRA', 'Sprint planning', 'User stories'], 'topics': ['Sprint ceremonies', 'Backlog grooming', 'Acceptance criteria', 'Product velocity'], 'goals': 'Execute product development with agile', 'project': 'Run a 2-week sprint simulation with user stories', 'duration': '3-4 weeks', 'difficulty': 'Intermediate'},
        {'phase': 'Product Metrics & Analytics', 'skills': ['Google Analytics', 'Mixpanel', 'A/B testing'], 'topics': ['AARRR metrics (Pirate Metrics)', 'Funnel analysis', 'Cohort analysis', 'Experimentation design'], 'goals': 'Measure and improve product performance', 'project': 'Build a product metrics dashboard', 'duration': '3-4 weeks', 'difficulty': 'Intermediate'},
        {'phase': 'Stakeholder Management & Communication', 'skills': ['Communication', 'Presentation', 'Negotiation'], 'topics': ['Executive communication', 'Stakeholder alignment', 'Trade-off decisions', 'Influence without authority'], 'goals': 'Work effectively with cross-functional teams', 'project': 'Present a product strategy to mock stakeholders', 'duration': '2-3 weeks', 'difficulty': 'Advanced'},
        {'phase': 'Portfolio & Case Studies', 'skills': ['Portfolio building', 'Product case studies', 'Storytelling'], 'topics': ['Documenting PM work', 'Product teardowns', 'Competitive analysis reports'], 'goals': 'Build a PM portfolio', 'project': 'Complete 3 product case studies', 'duration': '4-5 weeks', 'difficulty': 'Intermediate'},
        {'phase': 'Interview Preparation', 'skills': ['Product design questions', 'Metrics questions', 'Estimation'], 'topics': ['Design a product', 'Improve a metric', 'Behavioral STAR', 'Market sizing estimation'], 'goals': 'Crack PM interviews at top companies', 'project': 'Mock PM interviews with structured feedback', 'duration': '3-4 weeks', 'difficulty': 'Advanced'},
    ],
}

DEFAULT_ROADMAP = [
    {'phase': 'Foundations', 'skills': ['Programming basics', 'Problem solving'], 'topics': ['Variables', 'Loops', 'Functions', 'Data structures basics'], 'goals': 'Build programming fundamentals', 'project': 'Build a simple application', 'duration': '4 weeks', 'difficulty': 'Beginner'},
    {'phase': 'Core Skills', 'skills': ['Data structures', 'Algorithms', 'Databases'], 'topics': ['Arrays', 'Trees', 'SQL', 'Complexity'], 'goals': 'Master core CS concepts', 'project': 'Implement data structures', 'duration': '6 weeks', 'difficulty': 'Intermediate'},
    {'phase': 'Specialization', 'skills': ['Domain-specific tools', 'Frameworks'], 'topics': ['Choose your path', 'Build projects'], 'goals': 'Specialize in your field', 'project': 'Domain-specific project', 'duration': '8 weeks', 'difficulty': 'Advanced'},
    {'phase': 'Projects & Interview Prep', 'skills': ['Projects', 'Interview skills'], 'topics': ['Portfolio', 'Mock interviews', 'Resume'], 'goals': 'Prepare for job search', 'project': 'Complete portfolio projects', 'duration': '4 weeks', 'difficulty': 'Intermediate'},
]


class RoadmapAIService:
    """Service for generating personalized learning roadmaps."""
    
    def __init__(self):
        self.ai = AIService()
    
    def generate_roadmap(self, target_career, current_skills, experience_level, study_hours_per_week, priorities=None):
        """
        Generate a personalized learning roadmap.
        """
        if self.ai.is_available:
            ai_roadmap = self._generate_ai_roadmap(target_career, current_skills, experience_level, study_hours_per_week, priorities)
            if ai_roadmap:
                return ai_roadmap
        
        return self._get_template_roadmap(target_career, current_skills)
    
    def _generate_ai_roadmap(self, target_career, current_skills, experience_level, study_hours_per_week, priorities=None):
        """Generate roadmap using OpenAI."""
        skills_str = ', '.join(current_skills) if current_skills else 'None'
        
        priorities_prompt = ""
        if priorities:
            priority_lines = []
            for p in priorities:
                gap_val = p.get('gap')
                gap_str = f" (Gap: {gap_val})" if gap_val else ""
                priority_lines.append(f"- {p.get('skill_name')} (Priority: {p.get('priority')}){gap_str}")
            priorities_str = "\n".join(priority_lines)
            priorities_prompt = f"\nSkill Gaps (Prioritized Learning Focus):\n{priorities_str}\n\nEnsure these missing or weak skills are explicitly targeted in the generated roadmap phases."
        
        prompt = f"""Create a personalized learning roadmap for someone who wants to become a {target_career}.

Current skills: {skills_str}
Experience level: {experience_level}
Available study time: {study_hours_per_week} hours per week{priorities_prompt}

Create a roadmap with 6-8 phases. Each phase should build on the previous one.

Respond as a JSON array with this structure:
[
  {{
    "phase": "Phase Name",
    "skills": ["skill1", "skill2"],
    "topics": ["topic1", "topic2"],
    "goals": "Learning goals for this phase",
    "project": "A suggested project",
    "duration": "X weeks",
    "difficulty": "Beginner|Intermediate|Advanced"
  }}
]

Adjust durations based on {study_hours_per_week} hours/week availability."""

        messages = [
            {"role": "system", "content": "You are an expert career coach creating learning roadmaps. Respond with valid JSON only."},
            {"role": "user", "content": prompt}
        ]
        
        result = self.ai.chat_completion_json(messages, temperature=0.7, max_tokens=2500)
        if isinstance(result, list) and len(result) > 0:
            # Validate structure
            valid = []
            for phase in result:
                if all(k in phase for k in ['phase', 'skills', 'topics', 'goals', 'project', 'duration', 'difficulty']):
                    valid.append(phase)
            if valid:
                return valid
        return None
    
    def _get_template_roadmap(self, target_career, current_skills):
        """Get a template roadmap based on career goal."""
        target_lower = (target_career or '').lower()
        
    def _get_template_roadmap(self, target_career, current_skills):
        """Get a template roadmap based on career goal with alias matching and dynamic template fallback."""
        target_lower = (target_career or '').lower()
        current_lower = [s.lower() for s in (current_skills or [])]

        aliases = [
            ('cad', 'cad'),
            ('autocad', 'cad'),
            ('solidworks', 'cad'),
            ('catia', 'cad'),
            ('drafting', 'cad'),
            ('mech', 'mechanical engineer'),
            ('mechanical', 'mechanical engineer'),
            ('robotics', 'robotics'),
            ('civil', 'civil engineer'),
            ('electrical', 'electrical engineer'),
            ('aerospace', 'aerospace engineer'),
            ('ux', 'ui/ux designer'),
            ('ui', 'ui/ux designer'),
            ('cyber', 'cybersecurity engineer'),
            ('cloud', 'cloud engineer'),
            ('product manager', 'product manager'),
            ('pm', 'product manager'),
            ('data sci', 'data scientist'),
            ('data ana', 'data analyst'),
            ('full stack', 'full stack developer'),
            ('web dev', 'full stack developer'),
            ('software', 'software engineer'),
            ('sde', 'software engineer'),
        ]

        selected_template = None
        for keyword, template_key in aliases:
            if keyword in target_lower and template_key in ROADMAP_TEMPLATES:
                selected_template = ROADMAP_TEMPLATES[template_key]
                break

        if not selected_template:
            for career_key, template in ROADMAP_TEMPLATES.items():
                if career_key in target_lower:
                    selected_template = template
                    break

        if not selected_template:
            selected_template = [
                {'phase': f'{target_career} Foundations', 'skills': [f'{target_career} Core Basics', 'Fundamentals'], 'topics': ['Core concepts', 'Principles', 'Workflows'], 'goals': f'Build strong foundations in {target_career}', 'project': f'Build a foundational project in {target_career}', 'duration': '3-4 weeks', 'difficulty': 'Beginner'},
                {'phase': f'{target_career} Core Skills', 'skills': [f'{target_career} Intermediate Tools', 'Frameworks'], 'topics': ['Standard Procedures', 'Architecture', 'Integrations'], 'goals': f'Master intermediate concepts of {target_career}', 'project': f'Create an intermediate {target_career} application', 'duration': '4-6 weeks', 'difficulty': 'Intermediate'},
                {'phase': f'Advanced {target_career} & Optimization', 'skills': [f'Advanced {target_career}', 'Performance Optimization'], 'topics': ['Design Patterns', 'Scalability', 'Debugging'], 'goals': f'Master advanced techniques in {target_career}', 'project': f'Build an end-to-end {target_career} system', 'duration': '4-6 weeks', 'difficulty': 'Advanced'},
                {'phase': f'Projects & Interview Prep', 'skills': ['Portfolio Building', 'Interview Prep'], 'topics': ['Mock Interviews', 'Case Studies', 'Documentation'], 'goals': f'Prepare for professional roles in {target_career}', 'project': f'Complete portfolio projects for {target_career}', 'duration': '3-4 weeks', 'difficulty': 'Intermediate'},
            ]

        roadmap = []
        for phase in selected_template:
            phase_copy = phase.copy()
            phase_copy['completed_skills'] = [
                s for s in phase['skills'] if s.lower() in current_lower
            ]
            phase_copy['remaining_skills'] = [
                s for s in phase['skills'] if s.lower() not in current_lower
            ]
            roadmap.append(phase_copy)
        return roadmap

    
    def generate_course_guidance(self, career_goal, current_skills, degree, branch, academic_year, test_performance=None):
        """
        Generate personalized course guidance based on user profile.
        """
        if self.ai.is_available:
            ai_guidance = self._generate_ai_guidance(career_goal, current_skills, degree, branch, academic_year, test_performance)
            if ai_guidance:
                return ai_guidance
        
        return self._heuristic_guidance(career_goal, current_skills, test_performance)
    
    def _generate_ai_guidance(self, career_goal, current_skills, degree, branch, academic_year, test_performance):
        """Generate course guidance using OpenAI."""
        skills_str = ', '.join(current_skills) if current_skills else 'None'
        test_str = json.dumps(test_performance) if test_performance else 'No test data'
        
        prompt = f"""As a career advisor, recommend skills and courses for a student.

Career goal: {career_goal}
Current skills: {skills_str}
Degree: {degree}, Branch: {branch}
Academic year: {academic_year}
Test performance: {test_str}

Identify skill gaps and recommend 5-7 skills to learn. For each skill provide:
- name: The skill name
- why: Why it's required for this career
- priority: High/Medium/Low
- difficulty: Beginner/Intermediate/Advanced
- duration: Estimated learning time
- project: A suggested project to practice

Respond as a JSON array with this structure:
[
  {{
    "name": "Skill Name",
    "why": "Why it's needed",
    "priority": "High",
    "difficulty": "Beginner",
    "duration": "2-3 weeks",
    "project": "Suggested project"
  }}
]"""

        messages = [
            {"role": "system", "content": "You are an expert career advisor. Respond with valid JSON only."},
            {"role": "user", "content": prompt}
        ]
        
        result = self.ai.chat_completion_json(messages, temperature=0.7, max_tokens=2000)
        if isinstance(result, list) and len(result) > 0:
            valid = []
            for item in result:
                if all(k in item for k in ['name', 'why', 'priority', 'difficulty', 'duration', 'project']):
                    valid.append(item)
            if valid:
                return valid
        return None
    
    def _heuristic_guidance(self, career_goal, current_skills, test_performance=None):
        """Generate course guidance using heuristics."""
        target_lower = (career_goal or '').lower()
        current_lower = [s.lower() for s in current_skills]
        
        # Skill recommendations by career — CSE + non-CSE domains
        career_skills = {
            'data scientist': [
                {'name': 'Python', 'why': 'Primary language for data science and ML', 'priority': 'High', 'difficulty': 'Beginner', 'duration': '3-4 weeks', 'project': 'Data analysis pipeline'},
                {'name': 'SQL', 'why': 'Essential for data extraction and manipulation', 'priority': 'High', 'difficulty': 'Beginner', 'duration': '2-3 weeks', 'project': 'Build queries for a sample database'},
                {'name': 'Statistics', 'why': 'Foundation for understanding data distributions and ML algorithms', 'priority': 'High', 'difficulty': 'Intermediate', 'duration': '4-5 weeks', 'project': 'Statistical analysis of a dataset'},
                {'name': 'Pandas & NumPy', 'why': 'Core libraries for data manipulation in Python', 'priority': 'High', 'difficulty': 'Intermediate', 'duration': '3 weeks', 'project': 'Data cleaning and transformation pipeline'},
                {'name': 'Machine Learning', 'why': 'Core skill for building predictive models', 'priority': 'High', 'difficulty': 'Advanced', 'duration': '6-8 weeks', 'project': 'Build a predictive model end-to-end'},
                {'name': 'Data Visualization', 'why': 'Communicate insights effectively', 'priority': 'Medium', 'difficulty': 'Beginner', 'duration': '2-3 weeks', 'project': 'Create an interactive dashboard'},
                {'name': 'Deep Learning', 'why': 'Advanced ML for complex problems', 'priority': 'Medium', 'difficulty': 'Advanced', 'duration': '6-8 weeks', 'project': 'Image or text classification model'},
            ],
            'data analyst': [
                {'name': 'SQL', 'why': 'Essential for querying databases', 'priority': 'High', 'difficulty': 'Beginner', 'duration': '3 weeks', 'project': 'Complex queries for business analytics'},
                {'name': 'Excel', 'why': 'Widely used for quick analysis and reporting', 'priority': 'High', 'difficulty': 'Beginner', 'duration': '2 weeks', 'project': 'Build a comprehensive dashboard'},
                {'name': 'Python', 'why': 'For advanced data manipulation and automation', 'priority': 'High', 'difficulty': 'Intermediate', 'duration': '4 weeks', 'project': 'Automated data analysis script'},
                {'name': 'Tableau/Power BI', 'why': 'Create interactive dashboards for stakeholders', 'priority': 'High', 'difficulty': 'Intermediate', 'duration': '3 weeks', 'project': 'Build a business intelligence dashboard'},
                {'name': 'Statistics', 'why': 'Understand data distributions and significance', 'priority': 'Medium', 'difficulty': 'Intermediate', 'duration': '3-4 weeks', 'project': 'A/B test analysis'},
                {'name': 'Pandas', 'why': 'Efficient data manipulation in Python', 'priority': 'Medium', 'difficulty': 'Intermediate', 'duration': '2-3 weeks', 'project': 'Data cleaning pipeline'},
            ],
            'software engineer': [
                {'name': 'Data Structures', 'why': 'Foundation for efficient problem solving', 'priority': 'High', 'difficulty': 'Intermediate', 'duration': '4-6 weeks', 'project': 'Implement data structures from scratch'},
                {'name': 'Algorithms', 'why': 'Essential for coding interviews and optimization', 'priority': 'High', 'difficulty': 'Advanced', 'duration': '6-8 weeks', 'project': 'Solve 50+ problems on competitive platforms'},
                {'name': 'SQL', 'why': 'Required for most software engineering roles', 'priority': 'High', 'difficulty': 'Beginner', 'duration': '3 weeks', 'project': 'Design and query a database'},
                {'name': 'System Design', 'why': 'Critical for senior engineering roles', 'priority': 'Medium', 'difficulty': 'Advanced', 'duration': '4-6 weeks', 'project': 'Design a scalable system'},
                {'name': 'Git', 'why': 'Version control is essential for collaboration', 'priority': 'High', 'difficulty': 'Beginner', 'duration': '1-2 weeks', 'project': 'Contribute to an open-source project'},
                {'name': 'Web Development', 'why': 'Full-stack skills are in high demand', 'priority': 'Medium', 'difficulty': 'Intermediate', 'duration': '6-8 weeks', 'project': 'Build a full-stack web application'},
            ],
            'full stack': [
                {'name': 'JavaScript', 'why': 'Core language for web development', 'priority': 'High', 'difficulty': 'Intermediate', 'duration': '4 weeks', 'project': 'Build interactive web features'},
                {'name': 'React', 'why': 'Most popular frontend framework', 'priority': 'High', 'difficulty': 'Intermediate', 'duration': '4-6 weeks', 'project': 'Build a SPA with state management'},
                {'name': 'Node.js', 'why': 'JavaScript backend for full-stack development', 'priority': 'High', 'difficulty': 'Intermediate', 'duration': '3-4 weeks', 'project': 'Build a REST API'},
                {'name': 'SQL', 'why': 'Database management for web apps', 'priority': 'High', 'difficulty': 'Beginner', 'duration': '3 weeks', 'project': 'Design database schema for a web app'},
                {'name': 'Docker', 'why': 'Containerization for deployment', 'priority': 'Medium', 'difficulty': 'Intermediate', 'duration': '2-3 weeks', 'project': 'Dockerize your application'},
                {'name': 'TypeScript', 'why': 'Type safety for large applications', 'priority': 'Medium', 'difficulty': 'Intermediate', 'duration': '3 weeks', 'project': 'Migrate a JS project to TypeScript'},
            ],
            'mechanical': [
                {'name': 'CAD (SolidWorks/CATIA)', 'why': 'Essential 3D design tool for mechanical engineers', 'priority': 'High', 'difficulty': 'Beginner', 'duration': '4-5 weeks', 'project': 'Design a mechanical component'},
                {'name': 'Thermodynamics', 'why': 'Core subject for mechanical analysis and design', 'priority': 'High', 'difficulty': 'Intermediate', 'duration': '4-5 weeks', 'project': 'Thermal system analysis'},
                {'name': 'MATLAB', 'why': 'Used for simulations and engineering calculations', 'priority': 'High', 'difficulty': 'Intermediate', 'duration': '3-4 weeks', 'project': 'Simulate a dynamic system'},
                {'name': 'FEA (ANSYS)', 'why': 'Finite element analysis for structural simulation', 'priority': 'High', 'difficulty': 'Advanced', 'duration': '4-6 weeks', 'project': 'Stress analysis of a component'},
                {'name': 'Manufacturing Processes', 'why': 'Understanding how parts are made is critical for design', 'priority': 'High', 'difficulty': 'Intermediate', 'duration': '3-4 weeks', 'project': 'DFM analysis of a component'},
                {'name': 'Six Sigma / Lean', 'why': 'Quality and process improvement standard in manufacturing', 'priority': 'Medium', 'difficulty': 'Intermediate', 'duration': '3 weeks', 'project': 'Process improvement project'},
                {'name': 'PLC Programming', 'why': 'Essential for industrial automation roles', 'priority': 'Medium', 'difficulty': 'Intermediate', 'duration': '3-4 weeks', 'project': 'Automate a conveyor system'},
            ],
            'robotics': [
                {'name': 'ROS/ROS2', 'why': 'The standard framework for robot software development', 'priority': 'High', 'difficulty': 'Intermediate', 'duration': '5-7 weeks', 'project': 'Build a mobile robot simulation in Gazebo'},
                {'name': 'Python for Robotics', 'why': 'Primary scripting language in ROS and robot control', 'priority': 'High', 'difficulty': 'Beginner', 'duration': '3-4 weeks', 'project': 'Implement kinematics in Python'},
                {'name': 'Robot Kinematics', 'why': 'Fundamental for controlling robot motion', 'priority': 'High', 'difficulty': 'Intermediate', 'duration': '4-5 weeks', 'project': 'Forward/inverse kinematics solver'},
                {'name': 'OpenCV & Computer Vision', 'why': 'Vision is essential for robot perception', 'priority': 'High', 'difficulty': 'Intermediate', 'duration': '4-5 weeks', 'project': 'Object detection for robot grasping'},
                {'name': 'Path Planning Algorithms', 'why': 'Enables autonomous robot navigation', 'priority': 'High', 'difficulty': 'Advanced', 'duration': '4-5 weeks', 'project': 'Implement A* for robot navigation'},
                {'name': 'SLAM', 'why': 'Simultaneous Localization and Mapping for autonomous robots', 'priority': 'Medium', 'difficulty': 'Advanced', 'duration': '4-6 weeks', 'project': 'SLAM implementation in Gazebo'},
                {'name': 'Embedded Systems (Arduino/RPi)', 'why': 'Hardware control for physical robots', 'priority': 'Medium', 'difficulty': 'Intermediate', 'duration': '3-4 weeks', 'project': 'Build a line-following robot'},
            ],
            'civil': [
                {'name': 'AutoCAD', 'why': 'Standard drafting and design tool for civil engineers', 'priority': 'High', 'difficulty': 'Beginner', 'duration': '3-4 weeks', 'project': 'Create a site plan'},
                {'name': 'STAAD Pro / ETABS', 'why': 'Industry-standard structural analysis software', 'priority': 'High', 'difficulty': 'Intermediate', 'duration': '4-5 weeks', 'project': 'Analyze a building structure'},
                {'name': 'Structural Analysis', 'why': 'Core skill for designing safe structures', 'priority': 'High', 'difficulty': 'Intermediate', 'duration': '5-6 weeks', 'project': 'Analyze beams and frames'},
                {'name': 'Soil Mechanics', 'why': 'Essential for foundation design', 'priority': 'High', 'difficulty': 'Intermediate', 'duration': '4-5 weeks', 'project': 'Foundation design project'},
                {'name': 'Quantity Estimation (BOQ)', 'why': 'Core skill for project costing', 'priority': 'Medium', 'difficulty': 'Beginner', 'duration': '2-3 weeks', 'project': 'Prepare BOQ for a building'},
                {'name': 'Project Management (CPM/PERT)', 'why': 'Construction project scheduling', 'priority': 'Medium', 'difficulty': 'Intermediate', 'duration': '3-4 weeks', 'project': 'Create a project schedule'},
                {'name': 'Revit/BIM', 'why': 'Building Information Modeling is the future of civil engineering', 'priority': 'Medium', 'difficulty': 'Intermediate', 'duration': '4-5 weeks', 'project': 'Model a building in Revit'},
            ],
            'electrical': [
                {'name': 'Circuit Theory', 'why': 'Foundation of all electrical engineering', 'priority': 'High', 'difficulty': 'Beginner', 'duration': '3-4 weeks', 'project': 'Simulate circuits in LTSpice'},
                {'name': 'MATLAB/Simulink', 'why': 'Essential tool for electrical engineering simulations', 'priority': 'High', 'difficulty': 'Intermediate', 'duration': '3-4 weeks', 'project': 'Simulate a control system'},
                {'name': 'Power Systems', 'why': 'Critical for power sector and energy companies', 'priority': 'High', 'difficulty': 'Intermediate', 'duration': '5-6 weeks', 'project': 'Power flow analysis'},
                {'name': 'Control Systems', 'why': 'Fundamental for automation and embedded systems', 'priority': 'High', 'difficulty': 'Intermediate', 'duration': '4-5 weeks', 'project': 'PID controller design'},
                {'name': 'Embedded Systems (Microcontrollers)', 'why': 'Widely used in industry for automation', 'priority': 'Medium', 'difficulty': 'Intermediate', 'duration': '4-5 weeks', 'project': 'Build an embedded project'},
                {'name': 'PCB Design (KiCad)', 'why': 'Designing PCBs is a key hardware skill', 'priority': 'Medium', 'difficulty': 'Intermediate', 'duration': '3-4 weeks', 'project': 'Design and fabricate a PCB'},
                {'name': 'Signal Processing (DSP)', 'why': 'Fundamental for communication and control systems', 'priority': 'Medium', 'difficulty': 'Advanced', 'duration': '4-5 weeks', 'project': 'Design a digital filter'},
            ],
            'aerospace': [
                {'name': 'MATLAB/Simulink', 'why': 'Primary simulation tool in aerospace engineering', 'priority': 'High', 'difficulty': 'Intermediate', 'duration': '4-5 weeks', 'project': 'Flight dynamics simulation'},
                {'name': 'Aerodynamics (CFD)', 'why': 'Core skill for aircraft design and analysis', 'priority': 'High', 'difficulty': 'Advanced', 'duration': '5-7 weeks', 'project': 'Airfoil CFD analysis using OpenFOAM'},
                {'name': 'CATIA/SolidWorks', 'why': 'Standard CAD tools in aerospace industry', 'priority': 'High', 'difficulty': 'Intermediate', 'duration': '4-5 weeks', 'project': 'Aircraft component design'},
                {'name': 'Orbital Mechanics', 'why': 'Essential for space systems and satellite engineering', 'priority': 'High', 'difficulty': 'Advanced', 'duration': '4-5 weeks', 'project': 'Orbital transfer simulation'},
                {'name': 'Propulsion Systems', 'why': 'Core knowledge for jet engine and rocket design', 'priority': 'High', 'difficulty': 'Advanced', 'duration': '4-5 weeks', 'project': 'Gas turbine cycle analysis'},
                {'name': 'Flight Control Systems', 'why': 'Critical for aircraft stability and autopilot design', 'priority': 'Medium', 'difficulty': 'Advanced', 'duration': '4-5 weeks', 'project': 'Autopilot system in Simulink'},
                {'name': 'Composite Materials', 'why': 'Widely used in modern aerospace structures', 'priority': 'Medium', 'difficulty': 'Intermediate', 'duration': '3-4 weeks', 'project': 'Composite structure design report'},
            ],
            'ui/ux': [
                {'name': 'Figma', 'why': 'Industry standard design tool for UI/UX', 'priority': 'High', 'difficulty': 'Beginner', 'duration': '3-4 weeks', 'project': 'Design an app prototype in Figma'},
                {'name': 'User Research', 'why': 'Understanding users is the foundation of great UX', 'priority': 'High', 'difficulty': 'Beginner', 'duration': '2-3 weeks', 'project': 'Conduct user interviews and create personas'},
                {'name': 'Wireframing & Prototyping', 'why': 'Core design workflow skill', 'priority': 'High', 'difficulty': 'Beginner', 'duration': '3-4 weeks', 'project': 'Create low and high-fi prototypes'},
                {'name': 'Design Systems', 'why': 'Ensures consistency and scalability in design', 'priority': 'High', 'difficulty': 'Intermediate', 'duration': '3-4 weeks', 'project': 'Build a design system in Figma'},
                {'name': 'Usability Testing', 'why': 'Validates designs with real users', 'priority': 'High', 'difficulty': 'Intermediate', 'duration': '3-4 weeks', 'project': 'Run usability tests on your prototype'},
                {'name': 'Accessibility (WCAG)', 'why': 'Inclusive design is a professional requirement', 'priority': 'Medium', 'difficulty': 'Intermediate', 'duration': '2-3 weeks', 'project': 'Audit a website for accessibility'},
                {'name': 'Portfolio Building', 'why': 'UX roles require a strong portfolio of case studies', 'priority': 'Medium', 'difficulty': 'Beginner', 'duration': '4-6 weeks', 'project': 'Complete 3 UX case studies'},
            ],
            'cybersecurity': [
                {'name': 'Networking & TCP/IP', 'why': 'Foundation of all cybersecurity knowledge', 'priority': 'High', 'difficulty': 'Beginner', 'duration': '3-4 weeks', 'project': 'Analyze network traffic with Wireshark'},
                {'name': 'Linux & Bash', 'why': 'Most security tools run on Linux', 'priority': 'High', 'difficulty': 'Beginner', 'duration': '3-4 weeks', 'project': 'Automate security tasks with Bash'},
                {'name': 'Ethical Hacking (Kali Linux)', 'why': 'Core skill for penetration testing roles', 'priority': 'High', 'difficulty': 'Intermediate', 'duration': '5-7 weeks', 'project': 'Pentest a vulnerable VM'},
                {'name': 'OWASP Top 10 / Web Security', 'why': 'Web vulnerabilities are the most common attack vectors', 'priority': 'High', 'difficulty': 'Intermediate', 'duration': '4-5 weeks', 'project': 'Exploit and fix DVWA vulnerabilities'},
                {'name': 'Cryptography', 'why': 'Underlies all secure communication systems', 'priority': 'High', 'difficulty': 'Intermediate', 'duration': '3-4 weeks', 'project': 'Implement encryption/decryption programs'},
                {'name': 'SIEM & Incident Response', 'why': 'Core skill for SOC analyst roles', 'priority': 'Medium', 'difficulty': 'Advanced', 'duration': '4-5 weeks', 'project': 'Analyze a mock incident in Splunk'},
                {'name': 'CompTIA Security+ / CEH Certification', 'why': 'Industry-recognized certifications required by employers', 'priority': 'Medium', 'difficulty': 'Intermediate', 'duration': '5-8 weeks', 'project': 'Complete certification preparation'},
            ],
            'cloud': [
                {'name': 'AWS/Azure/GCP Core Services', 'why': 'Hands-on cloud services knowledge is essential', 'priority': 'High', 'difficulty': 'Beginner', 'duration': '5-6 weeks', 'project': 'Deploy a web app on AWS'},
                {'name': 'Terraform (IaC)', 'why': 'Infrastructure as Code is standard for cloud engineering', 'priority': 'High', 'difficulty': 'Intermediate', 'duration': '4-5 weeks', 'project': 'Provision infrastructure with Terraform'},
                {'name': 'Docker & Kubernetes', 'why': 'Container orchestration is core to modern cloud', 'priority': 'High', 'difficulty': 'Intermediate', 'duration': '5-6 weeks', 'project': 'Deploy a microservice on Kubernetes'},
                {'name': 'CI/CD Pipelines', 'why': 'Automates software delivery — must-have for cloud roles', 'priority': 'High', 'difficulty': 'Intermediate', 'duration': '3-4 weeks', 'project': 'Build a GitHub Actions CI/CD pipeline'},
                {'name': 'Cloud Security (IAM)', 'why': 'Security is the #1 responsibility in cloud engineering', 'priority': 'High', 'difficulty': 'Intermediate', 'duration': '3-4 weeks', 'project': 'Implement least privilege IAM policies'},
                {'name': 'Linux & Bash', 'why': 'Essential for managing cloud servers and automation', 'priority': 'Medium', 'difficulty': 'Beginner', 'duration': '2-3 weeks', 'project': 'Automate deployment with Bash scripts'},
                {'name': 'AWS Solutions Architect Certification', 'why': 'Most demanded cloud certification by employers', 'priority': 'Medium', 'difficulty': 'Advanced', 'duration': '5-8 weeks', 'project': 'Prepare for AWS SAA exam'},
            ],
            'product manager': [
                {'name': 'Product Strategy & Roadmapping', 'why': 'Core PM skill — defining vision and priorities', 'priority': 'High', 'difficulty': 'Intermediate', 'duration': '3-4 weeks', 'project': 'Create a 6-month product roadmap'},
                {'name': 'User Research', 'why': 'Understanding users is the foundation of great products', 'priority': 'High', 'difficulty': 'Beginner', 'duration': '2-3 weeks', 'project': 'Conduct user interviews and create personas'},
                {'name': 'Data Analytics (SQL/Google Analytics)', 'why': 'PMs need data to make informed decisions', 'priority': 'High', 'difficulty': 'Intermediate', 'duration': '3-4 weeks', 'project': 'Build a product metrics dashboard'},
                {'name': 'Agile/Scrum', 'why': 'Most tech companies use agile for product development', 'priority': 'High', 'difficulty': 'Beginner', 'duration': '2-3 weeks', 'project': 'Facilitate a sprint and write user stories'},
                {'name': 'A/B Testing & Experimentation', 'why': 'Data-driven decision making is a core PM skill', 'priority': 'High', 'difficulty': 'Intermediate', 'duration': '3-4 weeks', 'project': 'Design and analyze an A/B test'},
                {'name': 'Stakeholder Communication', 'why': 'PMs must align engineering, design, and business teams', 'priority': 'Medium', 'difficulty': 'Intermediate', 'duration': '2-3 weeks', 'project': 'Present a product strategy document'},
                {'name': 'Product Case Studies Portfolio', 'why': 'Required for PM interviews at top companies', 'priority': 'Medium', 'difficulty': 'Intermediate', 'duration': '4-5 weeks', 'project': 'Complete 3 PM case studies'},
            ],
        }
        
        # Domain keyword map for flexible matching
        domain_keywords = [
            ('mechanical', 'mechanical'),
            ('robotics', 'robotics'),
            ('robot', 'robotics'),
            ('civil', 'civil'),
            ('structural', 'civil'),
            ('construction', 'civil'),
            ('electrical', 'electrical'),
            ('electronics', 'electrical'),
            ('vlsi', 'electrical'),
            ('aerospace', 'aerospace'),
            ('aeronautical', 'aerospace'),
            ('aviation', 'aerospace'),
            ('spacecraft', 'aerospace'),
            ('ui/ux', 'ui/ux'),
            ('ux design', 'ui/ux'),
            ('ui design', 'ui/ux'),
            ('product design', 'ui/ux'),
            ('interaction design', 'ui/ux'),
            ('cybersecurity', 'cybersecurity'),
            ('cyber security', 'cybersecurity'),
            ('security engineer', 'cybersecurity'),
            ('ethical hack', 'cybersecurity'),
            ('penetration', 'cybersecurity'),
            ('cloud', 'cloud'),
            ('devops', 'devops engineer'),
            ('product manager', 'product manager'),
            ('product management', 'product manager'),
            ('data scientist', 'data scientist'),
            ('data analyst', 'data analyst'),
            ('software engineer', 'software engineer'),
            ('software developer', 'software engineer'),
            ('full stack', 'full stack'),
            ('fullstack', 'full stack'),
        ]
        
        recommendations = None
        for keyword, career_key in domain_keywords:
            if keyword in target_lower:
                recommendations = career_skills.get(career_key)
                if recommendations:
                    break
        
        if not recommendations:
            recommendations = [
                {'name': 'Problem Solving', 'why': 'Core skill for any engineering or tech career', 'priority': 'High', 'difficulty': 'Beginner', 'duration': '4 weeks', 'project': 'Solve domain-specific problems'},
                {'name': 'MATLAB / Python', 'why': 'Widely used in engineering and analysis roles', 'priority': 'High', 'difficulty': 'Beginner', 'duration': '3-4 weeks', 'project': 'Implement a simulation'},
                {'name': 'Technical Report Writing', 'why': 'Essential for all engineering disciplines', 'priority': 'High', 'difficulty': 'Beginner', 'duration': '2 weeks', 'project': 'Write a technical report for a project'},
                {'name': 'Project Management', 'why': 'Critical for career growth in any field', 'priority': 'Medium', 'difficulty': 'Beginner', 'duration': '3 weeks', 'project': 'Plan and execute a small project'},
                {'name': 'Communication & Presentation', 'why': 'Key to professional success in any career', 'priority': 'Medium', 'difficulty': 'Beginner', 'duration': 'Ongoing', 'project': 'Present a technical topic to an audience'},
            ]
        
        # Filter out already-acquired skills
        filtered = [rec for rec in recommendations if rec['name'].lower() not in current_lower]
        
        # Add test-based recommendations
        if test_performance:
            for topic, accuracy in test_performance.items():
                if accuracy < 60:
                    filtered.append({
                        'name': f'{topic} (Review)',
                        'why': f'Your test score in {topic} was {accuracy}% — review needed',
                        'priority': 'High',
                        'difficulty': 'Beginner',
                        'duration': '1-2 weeks',
                        'project': f'Practice {topic} problems',
                    })
        
        return filtered[:7] if filtered else recommendations

    def generate_phase_quiz(self, phase_name, skills, topics, difficulty='Beginner', num_questions=10):
        """
        Generate MCQ quiz questions for a specific roadmap phase.
        Ensures options are randomly shuffled for every question on every attempt.
        """
        questions = None
        if self.ai.is_available:
            questions = self._generate_ai_phase_quiz(phase_name, skills, topics, difficulty, num_questions)
        
        if not questions:
            questions = self._fallback_phase_quiz(phase_name, skills, topics, num_questions)

        # Shuffle options randomly per question while preserving correct answer text mapping
        shuffled_questions = []
        for q in questions:
            q_copy = dict(q)
            opts = list(q_copy['options'])
            correct_idx = q_copy['correct']
            if 0 <= correct_idx < len(opts):
                correct_text = opts[correct_idx]
                random.shuffle(opts)
                q_copy['options'] = opts
                q_copy['correct'] = opts.index(correct_text)
            shuffled_questions.append(q_copy)

        return shuffled_questions

    def _generate_ai_phase_quiz(self, phase_name, skills, topics, difficulty, num_questions):
        """Generate phase quiz questions using OpenAI."""
        skills_str = ', '.join(skills) if skills else phase_name
        topics_str = ', '.join(topics) if topics else phase_name

        prompt = f"""Create {num_questions} multiple-choice quiz questions to test knowledge of the
"{phase_name}" learning phase.

Skills covered: {skills_str}
Topics covered: {topics_str}
Difficulty: {difficulty}

Respond ONLY with a valid JSON array. Each element must have EXACTLY this structure:
{{
  "question": "The question text",
  "options": ["Option A", "Option B", "Option C", "Option D"],
  "correct": 0,
  "topic": "relevant topic name"
}}

Rules:
- "correct" is the 0-based index of the correct option in "options" (0, 1, 2, or 3).
- Questions must be practical and test real understanding, not trivia.
- Vary the topics across questions.
- Do not add any text outside the JSON array."""

        messages = [
            {"role": "system", "content": "You are an expert quiz maker. Respond with valid JSON only."},
            {"role": "user", "content": prompt},
        ]

        result = self.ai.chat_completion_json(messages, temperature=0.7, max_tokens=3000)
        if isinstance(result, list) and len(result) > 0:
            valid = []
            for q in result:
                if (
                    isinstance(q, dict)
                    and all(k in q for k in ['question', 'options', 'correct', 'topic'])
                    and isinstance(q['options'], list)
                    and len(q['options']) == 4
                    and isinstance(q['correct'], int)
                    and 0 <= q['correct'] <= 3
                ):
                    valid.append(q)
            if valid:
                return valid[:num_questions]
        return None

    def _fallback_phase_quiz(self, phase_name, skills, topics, num_questions):
        """Return phase-specific questions when AI is unavailable."""
        bank = []
        for skill in (skills or [phase_name])[:5]:
            bank.append({
                'question': f"What is the primary role of {skill} in the '{phase_name}' phase?",
                'options': [
                    f"To provide core tools and functionality for {skill} within {phase_name}.",
                    f"{skill} is deprecated and no longer utilized in engineering.",
                    f"{skill} is strictly used for offline file compression.",
                    f"{skill} has no practical application in modern workflows.",
                ],
                'correct': 0,
                'topic': skill,
            })
        for topic in (topics or [])[:5]:
            bank.append({
                'question': f"How does '{topic}' apply to mastering {phase_name}?",
                'options': [
                    f"It represents a core technical principle and workflow in {phase_name}.",
                    f"It is an optional third-party tool with no standards compliance.",
                    f"It is an obsolete concept replaced by legacy manual procedures.",
                    f"It applies only to non-technical administrative tasks.",
                ],
                'correct': 0,
                'topic': topic,
            })
        while len(bank) < num_questions:
            bank.append({
                'question': f"What is a primary learning objective of completing the '{phase_name}' training phase?",
                'options': [
                    f"Gaining hands-on proficiency in {phase_name} and delivering practical projects.",
                    "Memorizing theory without executing real-world projects.",
                    "Bypassing foundational standards and principles.",
                    "Disregarding industry quality assurance checks.",
                ],
                'correct': 0,
                'topic': phase_name,
            })
        return bank[:num_questions]


