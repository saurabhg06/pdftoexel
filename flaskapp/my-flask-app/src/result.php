<?php
session_start();

// Simple in-memory storage (in real application, use database)
$results = isset($_SESSION['results']) ? $_SESSION['results'] : [];

// Process form submission
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $result = [
        'roll_no' => $_POST['roll_no'],
        'name' => $_POST['name'],
        'marks' => [
            'math' => (int)$_POST['math'],
            'science' => (int)$_POST['science'],
            'english' => (int)$_POST['english']
        ]
    ];
    
    // Calculate total and percentage
    $result['total'] = array_sum($result['marks']);
    $result['percentage'] = ($result['total'] / 300) * 100;
    
    // Store result
    $results[] = $result;
    $_SESSION['results'] = $results;
}
?>

<!DOCTYPE html>
<html>
<head>
    <title>Student Result Analysis</title>
    <style>
        body { font-family: Arial; margin: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        .form-group { margin: 10px 0; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Student Result Entry</h2>
        <form method="POST">
            <div class="form-group">
                <label>Roll No:</label>
                <input type="text" name="roll_no" required>
            </div>
            <div class="form-group">
                <label>Name:</label>
                <input type="text" name="name" required>
            </div>
            <div class="form-group">
                <label>Math:</label>
                <input type="number" name="math" max="100" required>
            </div>
            <div class="form-group">
                <label>Science:</label>
                <input type="number" name="science" max="100" required>
            </div>
            <div class="form-group">
                <label>English:</label>
                <input type="number" name="english" max="100" required>
            </div>
            <button type="submit">Submit Result</button>
        </form>

        <h2>Results Analysis</h2>
        <table>
            <tr>
                <th>Roll No</th>
                <th>Name</th>
                <th>Math</th>
                <th>Science</th>
                <th>English</th>
                <th>Total</th>
                <th>Percentage</th>
            </tr>
            <?php foreach ($results as $result): ?>
            <tr>
                <td><?php echo htmlspecialchars($result['roll_no']); ?></td>
                <td><?php echo htmlspecialchars($result['name']); ?></td>
                <td><?php echo $result['marks']['math']; ?></td>
                <td><?php echo $result['marks']['science']; ?></td>
                <td><?php echo $result['marks']['english']; ?></td>
                <td><?php echo $result['total']; ?></td>
                <td><?php echo number_format($result['percentage'], 2); ?>%</td>
            </tr>
            <?php endforeach; ?>
        </table>
    </div>
</body>
</html>