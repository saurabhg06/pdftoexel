import pandas as pd
import json

# Load the Excel file
file_path = "output19.xlsx"  # Update the file path if necessary
xls = pd.ExcelFile(file_path)

# Load the sheet into a DataFrame
df = pd.read_excel(xls, sheet_name=xls.sheet_names[0])

# Function to extract semester numbers
def extract_semester_number(semester_text):
    if "FIRST" in semester_text.upper():
        return 1
    elif "SECOND" in semester_text.upper():
        return 2
    elif "THIRD" in semester_text.upper():
        return 3
    elif "FOURTH" in semester_text.upper():
        return 4
    elif "FIFTH" in semester_text.upper():
        return 5
    elif "SIXTH" in semester_text.upper():
        return 6
    else:
        return None

df["Semester Number"] = df["Semester"].apply(extract_semester_number)

# Aggregate marks semester-wise for each student
student_total_marks = df.groupby(["Course Name", "Enrollment Number", "Semester Number"])["Total Marks"].sum().reset_index()

# Merge to get student details
df_merged = df.drop(columns=["Total Marks"]).drop_duplicates(subset=["Course Name", "Enrollment Number", "Semester Number"])
df_merged = df_merged.merge(student_total_marks, on=["Course Name", "Enrollment Number", "Semester Number"], how="left")

# Compute year-wise total marks for each student
df_merged["Year"] = df_merged["Semester Number"].apply(lambda x: "First Year" if x in [1, 2] else ("Second Year" if x in [3, 4] else "Third Year"))
df_yearly = df_merged.groupby(["Course Name", "Enrollment Number", "Year"]).agg({
    "Total Marks": "sum",
    "Student Name": "first",
}).reset_index()

# Identifying toppers (highest total marks per course and year)
toppers = df_yearly.sort_values(["Course Name", "Year", "Total Marks"], ascending=[True, True, False])
toppers = toppers.groupby(["Course Name", "Year"]).head(3)  # Get top 3 per course per year

# Save toppers in JSON format
toppers_json_path = "toppers.json"
toppers.to_json(toppers_json_path, orient="records", indent=4)

# Semester-wise and course-wise result analysis
result_analysis = {}
for (course, semester), group in df.groupby(["Course Name", "Semester"]):
    total_students = len(group)
    distinction = len(group[group["Result Status"].str.contains("DIST.", na=False)]) # 75%+ is Distinction
    first_class = len(group[group["Result Status"].str.contains("FIRST CLASS", na=False)])
    second_class = len(group[group["Result Status"].str.contains("SECOND CLASS", na=False)])
    fail = len(group[group["Result Status"].str.contains("F.T.", na=False)])
    atkt = len(group[group["Result Status"].str.contains("A.T.K.T.", na=False)])
    passed = total_students - fail
    first_class_or_more = distinction + first_class

    result_analysis.setdefault(course, {})[semester] = {
        "Total Students": total_students,
        "Distinction": distinction,
        "First Class": first_class,
        "First Class or More": first_class_or_more,
        "Second Class": second_class,
        "Fail": fail,
        "ATKT": atkt,
        "Pass": passed,
        "Pass Percentage": round((passed / total_students) * 100, 2) if total_students > 0 else 0
    }

# Save result analysis in JSON format
result_analysis_json_path = "result_analysis_semester_wise.json"
with open(result_analysis_json_path, "w") as json_file:
    json.dump(result_analysis, json_file, indent=4)

print("Toppers JSON saved at:", toppers_json_path)
print("Result Analysis JSON saved at:", result_analysis_json_path)
