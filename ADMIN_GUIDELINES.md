# Admin Platform Guide - English Professional

This guide provides step-by-step instructions for instructors and administrators to manage courses, quizzes, forums, and users via the Django Admin interface.

## 1. Accessing the Admin Panel

*   **URL**: Navigate to `/admin/` in your browser (e.g., `http://localhost:8000/admin/` or your production domain).
*   **Login**: Enter your superuser or staff credentials.
*   **Dashboard**: Upon logging in, you will see the "English Professional Admin" dashboard listing all available applications.

---

## 2. Course Management

Located under the **COURSES** section.

### Creating & Editing Courses
1.  Click **Courses**.
2.  Click **Add Course** (top right) or select an existing course to edit.
3.  **Key Fields**:
    *   **Title & Description**: Enter the course details.
    *   **Instructors**: Select instructors from the list. *Tip: Hold `Ctrl` (Windows) or `Cmd` (Mac) to select multiple instructors.*
4.  **Adding Lessons (Inline)**:
    *   You do not need to leave the Course page to add lessons. Scroll to the bottom to find the **Lessons** section.
    *   Click **Add another Lesson**.
    *   Enter the **Title**, **Order** (e.g., 1, 2, 3), and content.
5.  Click **Save**.

### Managing Assignments
1.  Click **Assignments** under the Courses section.
2.  Link the assignment to a specific **Lesson**.
3.  Set the **Due date**.

### Grading & Plagiarism
1.  Click **Submissions**.
2.  **Filters**: Use the sidebar on the right to filter by **Assignment**, **Student**, or **Plagiarism status**.
3.  **Plagiarism Report**:
    *   Open a student's submission.
    *   Scroll to the **Plagiarism report** section (Inline).
    *   You can view the **Score**, **Is plagiarized** status, and the **Report URL**.
    *   *Note: These fields are read-only and populated by the system.*

---

## 3. Quiz Management

Located under the **QUIZ** section.

### Step 1: Question Banks
Before creating a quiz, organize your questions into banks.
1.  Click **Question banks**.
2.  Create a bank (e.g., "Module 1 Grammar") and link it to a **Course**.
3.  **Add Questions**: You can add questions directly inside the Question Bank page using the inline form.

### Step 2: Managing Questions & Choices
If you need to add more details to questions:
1.  Click **Questions**.
2.  **Question Type**: Select Single Choice, Multiple Choice, etc.
3.  **Choices**: At the bottom of the Question page, add the possible answers and mark the **Correct** one.

### Step 3: Creating the Quiz
1.  Click **Quizzes**.
2.  **Configuration**:
    *   **Course**: The course this quiz belongs to.
    *   **Question Bank**: The source of questions.
    *   **Duration**: Time limit in minutes.
    *   **Number of questions**: How many questions to pull from the bank.
    *   **Points per question**: Score value for each question.

### Viewing Student Results
1.  Click **Quiz submissions**.
2.  **Overview**: The list view shows the **Score (%)**, **Total Score**, and **Time Taken**.
3.  **Detailed Review**: Click on a submission ID to see exactly when they started and ended.
4.  **Question Attempts**: To see exactly which option a student chose for a specific question, go to the **Quiz question attempts** section.

---

## 4. Forum Moderation

Located under the **FORUM** section.

### Managing Threads
1.  Click **Discussion threads**.
2.  **Moderation Tools**:
    *   **Is Pinned**: Check this to keep the thread at the top of the list.
    *   **Is Locked**: Check this to prevent students from replying.
3.  **Replies**: You can view and manage posts directly within the Thread page.

### Managing Posts
1.  Click **Discussion posts**.
2.  **Is Solution**: You can mark a helpful post as the "Solution" so it is highlighted in the forum.
3.  **Search**: Use the search bar to find posts containing specific keywords or by specific authors.

---

## 5. General Tips

*   **Search**: Almost every page has a search bar at the top. Use it to find specific Students, Courses, or Titles.
*   **Filters**: Look at the right sidebar. It allows you to filter lists (e.g., "Show only Plagiarized submissions" or "Show Quizzes for Course X").
*   **Bulk Actions**:
    1.  Select multiple items using the checkboxes on the left.
    2.  Click the **Action** dropdown at the top (e.g., "Delete selected stories").
    3.  Click **Go**.
*   **Date Hierarchy**: In sections like Quiz Submissions, you can drill down by year, month, and day using the date links at the top of the list.

---

*Generated for English Professional Platform*