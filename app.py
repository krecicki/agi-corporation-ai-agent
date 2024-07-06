import random
import datetime
import openai
from typing import List, Dict

# Set your OpenAI API key here
openai.api_key = ''

class Task:
    def __init__(self, description: str, duration: int, dependencies: List[str] = None):
        self.description = description
        self.duration = duration
        self.dependencies = dependencies or []
        self.status = "Not Started"
        self.progress = 0

    def update_progress(self, progress: int):
        self.progress += progress
        if self.progress >= 100:
            self.status = "Completed"
            self.progress = 100
        elif self.progress > 0:
            self.status = "In Progress"

class Employee:
    def __init__(self, name: str, role: str, skills: List[str]):
        self.name = name
        self.role = role
        self.skills = skills
        self.current_task = None

    def assign_task(self, task: Task):
        self.current_task = task
        task.status = "In Progress"

    def work_on_task(self):
        if self.current_task:
            progress = random.randint(10, 30)
            self.current_task.update_progress(progress)
            return f"{self.name} made {progress}% progress on {self.current_task.description}"
        return f"{self.name} is currently unassigned"

class Department:
    def __init__(self, name: str):
        self.name = name
        self.employees: List[Employee] = []
        self.tasks: List[Task] = []
        self.completed_tasks: List[Task] = []
        self.reports: List[str] = []

    def add_employee(self, employee: Employee):
        self.employees.append(employee)

    def add_task(self, task: Task):
        self.tasks.append(task)

    def assign_tasks(self):
        for employee in self.employees:
            if not employee.current_task:
                available_tasks = [task for task in self.tasks if task.status == "Not Started" and all(dep in [t.description for t in self.completed_tasks] for dep in task.dependencies)]
                if available_tasks:
                    task = random.choice(available_tasks)
                    employee.assign_task(task)

    def work_day(self):
        daily_report = f"Daily Report for {self.name}:\n"
        for employee in self.employees:
            result = employee.work_on_task()
            daily_report += f"- {result}\n"
            if employee.current_task and employee.current_task.status == "Completed":
                self.completed_tasks.append(employee.current_task)
                self.tasks.remove(employee.current_task)
                employee.current_task = None
        self.assign_tasks()
        self.reports.append(daily_report)
        return daily_report

    def generate_status_report(self):
        return f"Status Report for {self.name}:\n" + \
               f"Completed Tasks: {len(self.completed_tasks)}\n" + \
               f"Remaining Tasks: {len(self.tasks)}\n" + \
               f"Employee Utilization: {sum(1 for e in self.employees if e.current_task)}/{len(self.employees)}"

    def ask_ai_assistant(self, question: str):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an AI assistant helping with product launch strategies."},
                    {"role": "user", "content": question}
                ]
            )
            return response.choices[0].message['content']
        except Exception as e:
            return f"Error in AI response: {str(e)}"

class CEO:
    def __init__(self, name: str):
        self.name = name
        self.departments: Dict[str, Department] = {}
        self.product_launch_date = None

    def add_department(self, department: Department):
        self.departments[department.name] = department

    def set_product_launch_date(self, date: datetime.date):
        self.product_launch_date = date

    def review_reports(self):
        overall_report = f"CEO {self.name}'s Overall Report:\n"
        for dept_name, department in self.departments.items():
            overall_report += f"\n{department.generate_status_report()}\n"
        return overall_report

    def make_decision(self):
        total_tasks = sum(len(dept.tasks) + len(dept.completed_tasks) for dept in self.departments.values())
        completed_tasks = sum(len(dept.completed_tasks) for dept in self.departments.values())
        progress_percentage = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0

        question = f"Given a product launch with {progress_percentage:.1f}% completion and {(self.product_launch_date - datetime.date.today()).days} days left, what decision should be made?"
        ai_response = self.departments["Product Development"].ask_ai_assistant(question)
        
        return ai_response

def generate_product_details(product_idea: str) -> Dict:
    prompt = f"""
    Based on the product idea "{product_idea}", generate a detailed product description including:
    1. Product name
    2. Brief description
    3. Key features (list at least 3)
    4. Target market
    5. Estimated development time (in weeks)
    6. Potential challenges

    Format the response as a Python dictionary.
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an AI assistant helping to generate product details for a new product launch."},
                {"role": "user", "content": prompt}
            ]
        )
        return eval(response.choices[0].message['content'])
    except Exception as e:
        print(f"Error generating product details: {str(e)}")
        return {
            "name": product_idea,
            "description": "A innovative new product",
            "key_features": ["Feature 1", "Feature 2", "Feature 3"],
            "target_market": "General consumers",
            "estimated_development_time": 12,
            "potential_challenges": ["Market competition", "Technical complexity", "User adoption"]
        }

def generate_tasks_for_product(product_details: Dict) -> Dict[str, List[Task]]:
    prompt = f"""
    Generate a list of tasks for launching the product "{product_details['name']}".
    Consider the following details:
    - Description: {product_details['description']}
    - Key features: {', '.join(product_details['key_features'])}
    - Target market: {product_details['target_market']}
    - Estimated development time: {product_details['estimated_development_time']} weeks
    - Potential challenges: {', '.join(product_details['potential_challenges'])}

    Include tasks for Product Development, Marketing, Sales, and Customer Support departments.
    For each task, provide a brief description and estimated duration in days.
    Format the response as a Python dictionary where keys are department names and values are lists of tuples (task_description, duration_in_days).
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an AI assistant helping to generate tasks for a product launch."},
                {"role": "user", "content": prompt}
            ]
        )
        tasks_dict = eval(response.choices[0].message['content'])
        return {dept: [Task(desc, duration) for desc, duration in task_list] for dept, task_list in tasks_dict.items()}
    except Exception as e:
        print(f"Error generating tasks: {str(e)}")
        # Fallback to predefined tasks if AI generation fails
        return {
            "Product Development": [
                Task(f"Finalize {product_details['name']} features", 5),
                Task(f"Conduct internal testing for {product_details['name']}", 3, [f"Finalize {product_details['name']} features"]),
                Task(f"Develop {product_details['name']} user manual", 4, [f"Finalize {product_details['name']} features"]),
            ],
            "Marketing": [
                Task(f"Develop marketing strategy for {product_details['name']}", 4),
                Task(f"Create promotional materials for {product_details['name']}", 3, [f"Develop marketing strategy for {product_details['name']}"]),
                Task(f"Plan launch event for {product_details['name']}", 5, [f"Create promotional materials for {product_details['name']}"]),
            ],
            "Sales": [
                Task(f"Prepare sales pitch for {product_details['name']}", 2),
                Task(f"Contact potential clients for {product_details['name']}", 5, [f"Prepare sales pitch for {product_details['name']}"]),
                Task(f"Develop pricing strategy for {product_details['name']}", 3),
            ],
            "Customer Support": [
                Task(f"Set up support infrastructure for {product_details['name']}", 4),
                Task(f"Train support team on {product_details['name']}", 3, [f"Set up support infrastructure for {product_details['name']}"]),
                Task(f"Create FAQs for {product_details['name']}", 2, [f"Train support team on {product_details['name']}"]),
            ]
        }

def simulate_product_launch(product_idea: str):
    product_details = generate_product_details(product_idea)
    print(f"Initiating launch simulation for product: {product_details['name']}")
    print("Product Details:")
    for key, value in product_details.items():
        print(f"{key.capitalize()}: {value}")
    print("\n")

    # Initialize CEO and Departments
    ceo = CEO("John Doe")
    departments = {
        "Product Development": Department("Product Development"),
        "Marketing": Department("Marketing"),
        "Sales": Department("Sales"),
        "Customer Support": Department("Customer Support")
    }

    for dept in departments.values():
        ceo.add_department(dept)

    # Add employees to departments
    departments["Product Development"].add_employee(Employee("Alice", "Lead Developer", ["Python", "Project Management"]))
    departments["Product Development"].add_employee(Employee("Bob", "QA Engineer", ["Testing", "Automation"]))
    departments["Marketing"].add_employee(Employee("Charlie", "Marketing Manager", ["Digital Marketing", "Content Creation"]))
    departments["Sales"].add_employee(Employee("Diana", "Sales Representative", ["Negotiation", "Client Relations"]))
    departments["Customer Support"].add_employee(Employee("Eve", "Support Specialist", ["Technical Support", "Communication"]))

    # Generate and add tasks for the specific product
    tasks = generate_tasks_for_product(product_details)
    for dept_name, dept_tasks in tasks.items():
        for task in dept_tasks:
            departments[dept_name].add_task(task)

    # Set product launch date based on estimated development time
    launch_days = product_details['estimated_development_time'] * 7  # convert weeks to days
    ceo.set_product_launch_date(datetime.date.today() + datetime.timedelta(days=launch_days))

    # Simulate the product launch process
    for day in range(1, launch_days + 1):
        print(f"\nDay {day}:")
        for dept in departments.values():
            print(dept.work_day())
        
        if day % 7 == 0:  # Weekly CEO review
            print("\nWeekly CEO Review:")
            print(ceo.review_reports())
            decision = ceo.make_decision()
            print(f"CEO Decision: {decision}")

            if "delay" in decision.lower():
                ceo.set_product_launch_date(ceo.product_launch_date + datetime.timedelta(days=14))
                print(f"New product launch date: {ceo.product_launch_date}")

    print("\nFinal CEO Review:")
    print(ceo.review_reports())

    # Generate board report
    board_report = generate_board_report(ceo, product_details)
    print("\nBoard Report:")
    print(board_report)

def generate_board_report(ceo: CEO, product_details: Dict) -> str:
    total_tasks = sum(len(dept.tasks) + len(dept.completed_tasks) for dept in ceo.departments.values())
    completed_tasks = sum(len(dept.completed_tasks) for dept in ceo.departments.values())
    progress_percentage = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0

    prompt = f"""
    Generate a concise board report for the launch of {product_details['name']}.
    Product details:
    - Description: {product_details['description']}
    - Key features: {', '.join(product_details['key_features'])}
    - Target market: {product_details['target_market']}
    - Potential challenges: {', '.join(product_details['potential_challenges'])}
    
    Overall progress is {progress_percentage:.1f}%, launch date is {ceo.product_launch_date}.
    Include sections for department status, key achievements, critical pending tasks,
    risk assessment, recommendation, and next action.
    """

    try:
        response = ceo.departments["Product Development"].ask_ai_assistant(prompt)
        return response
    except Exception as e:
        print(f"Error generating board report: {str(e)}")
        return "Error occurred while generating the board report."

if __name__ == "__main__":
    product_idea = input("Enter your product idea: ")
    simulate_product_launch(product_idea)
