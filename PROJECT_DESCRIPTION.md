# Peer Skill Swap Platform

**Role**: Full-Stack Developer  
**Technologies Used**: Python, Django, SQLite (Development), PostgreSQL (Production), HTML5, CSS3, Bootstrap 5, Django ORM, django-crispy-forms.

## 📌 Project Purpose
The Peer Skill Swap Platform is a modern, community-driven web application designed to democratize education. It provides a credit-based marketplace where users can exchange their knowledge by offering skills they can teach in return for learning skills they desire. This project tackles the barrier of expensive private tutoring by empowering individuals to leverage their existing expertise as currency.

## 🚀 Key Features

*   **Custom Authentication and Profiles**: Implemented a secure registration system using Django’s authentication framework with extended custom user profiles containing personal bios, skills, and virtual credits.
*   **Skill Matching Algorithm**: Engineered an intelligent backend matching system using Django’s ORM to automatically connect users with complementary teaching and learning interests, avoiding duplicate results.
*   **Virtual Credit System**: Designed an economic loop where users earn credits by successfully teaching others and spend credits to attend learning sessions, incentivizing active participation.
*   **Session Booking & Management**: Developed a comprehensive scheduling system allowing students to request sessions with teachers, and empowering teachers to accept or reject them.
*   **In-app Messaging**: Built an internal communication system allowing users to chat securely and coordinate sessions directly on the platform without exchanging external contact information.
*   **Review & Rating System**: Created a post-session evaluation mechanism that finalizes the exchange of credits and promotes trust within the community.
*   **Responsive User Interface**: Crafted a sleek, intuitive frontend leveraging Bootstrap 5 methodologies, ensuring seamless user experiences across desktop and mobile devices.

## 📈 Technical Impact & Highlights
*   Architected a modular and loosely coupled system using specialized Django apps (`accounts`, `skills`, `bookings`, `messaging`) emphasizing scalability and maintainable codebases.
*   Deployed optimized complex queries using `select_related` and robust filtering to minimize database latency within the matchmaking algorithm.
*   Leveraged strict model validation and robust form handling using `django-crispy-forms` to ensure secure user input.
*   Reduced friction in the user journey by designing a centralized dashboard that highlights actionable items, immediate matches, and urgent session requests in a single view.
