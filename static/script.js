function check(operation, problems, bottomMeasure, topMeasure) {

    // Massives for arbitrary pairs
    var massiv_a = [];
    var massiv_b = [];

    var correctAns = 0;
    var maxProblems;

    // Maximum amount of problems
    if (operation == 'div' || operation == 'lineeq') {
        maxProblems = 81;
    } else if (operation == 'mul') {
        maxProblems = 45;
    } else if (operation == 'quadeq') {
        maxProblems = 190;
    }

    var numberOfProblems = problems;

    if (!problems) {
        if (operation == 'add' || operation == 'sub') {
            do {
                numberOfProblems = prompt('How many problems do you want? You should choose at least one.');
            } while (isNaN(numberOfProblems) == true || numberOfProblems == 0);
        } else {
            do {
                numberOfProblems = prompt('How many problems do you want? You should choose at least one, but not more than '
                    + maxProblems + '.');
            } while (isNaN(numberOfProblems) == true || numberOfProblems == 0 || numberOfProblems > maxProblems);
        }
    }

    // Timestamp at the beginning
    var date1 = new Date();

    for (var i = 1; i <= numberOfProblems; ++i) {

        var a, b;
        var ans, ans2;

        // Addition
        if (operation == 'add') {
            do {
                a = randomInteger(bottomMeasure, parseInt(topMeasure, 10) - 1);
                b = randomInteger(bottomMeasure, parseInt(topMeasure, 10) - 1);
            } while (a + b > parseInt(topMeasure, 10) - 1 || checkPreviousAddMul(massiv_a, massiv_b, a, b));
            ans = +prompt(+i + '. Find ' + a + '+' + b + '=', '');
        }

        // Subtruction
        if (operation == 'sub') {
            do {
                a = randomInteger(bottomMeasure, parseInt(topMeasure, 10) - 1);
                b = randomInteger(bottomMeasure, parseInt(topMeasure, 10) - 1);
            } while (a - b <= 0 || checkPreviousAddMul(massiv_a, massiv_b, a, b));

            ans = +prompt(+i + '. Find ' + a + '-' + b + '=', '');
        }

        // Division
        if (operation == 'div') {
            do {
                a = randomInteger(1, 9);
                b = randomInteger(1, 9);
            } while (checkPreviousDiv(massiv_a, massiv_b, a, b));
            ans = +prompt(+i + '. Find ' + a * b + '/' + a + '=', '');
        }

        // Linear equation
        if (operation == 'lineeq') {
            do {
                a = randomInteger(1, 9);
                b = randomInteger(1, 9);
            } while (checkPreviousDiv(massiv_a, massiv_b, a, b));
            ans = +prompt(+i + '. Find x if ' + a + ' * x = ' + a * b, '');
        }

        // Multiplication
        if (operation == 'mul') {
            do {
                a = randomInteger(1, 9);
                b = randomInteger(1, 9);
            } while (checkPreviousAddMul(massiv_a, massiv_b, a, b));
            ans = +prompt(+i + '. Find ' + a + '*' + b + '=', '');
        }

        // Quadratic equation
        if (operation == 'quadeq') {
            do {
                a = randomInteger(-10, 10);
                b = randomInteger(-10, 10);
            } while (checkPreviousAddMul(massiv_a, massiv_b, a, b) || a * b == 0 || a + b == 0 || a == b);

            if (a + b < 0) {
                sign1 = '+';
            } else {
                sign1 = '-';
            }

            if (a + b == 1 || a + b == -1) {
                coef = '';
            } else {
                coef = Math.abs(a + b);
            }

            if (a * b > 0) {
                sign2 = '+';
            } else {
                sign2 = '-';
            }

            ans = +prompt(+i + '. Find the first solution of x^2' + sign1 + coef + 'x' + sign2 + Math.abs(a * b) + '= 0', '');
            ans2 = +prompt(+i + '. Find the second solution of of x^2' + sign1 + coef + 'x' + sign2 + Math.abs(a * b) + '= 0', '');
        }

        // If escape or cancel pressed brake the loop
        if (ans == 0) {
            break;
        }

        // Adds two random numbers a and b to massives
        massiv_a.push(a);
        massiv_b.push(b);

        // The variables to check results
        var div = a * b / a;
        var mul = a * b;
        var add = a + b;
        var sub = a - b;
        var lineeq = a * b / a;

        // The final timestamp
        if (i == numberOfProblems) {
            var date2 = new Date();
        }

        // Checks if user's answer is correct
        if (operation == 'quadeq') {
            if ((ans == a && ans2 == b) || (ans == b && ans2 == a)) {
                ++correctAns;
            } else {
                alert('Wrong. Correct answers are: ' + a + ' and ' + b + '.');
            }
        } else {
            var oper = eval(operation);
            if (oper == ans) {
                ++correctAns;
            } else {
                alert('Wrong. Correct answer is ' + oper + '.');
            }
        }
    }

    // Calculates time spent on problems
    var min = date2.getMinutes() - date1.getMinutes();
    var sec = date2.getSeconds() - date1.getSeconds();
    var milisec = date2.getMilliseconds() - date1.getMilliseconds();

    // Time corrections if needed
    if (milisec < 0) {
        milisec = milisec + 1000;
        sec = sec - 1;
    }
    if (sec < 0) {
        sec = sec + 60;
        min = min - 1;
    }
    if (min < 0) {
        min = min + 60;
    }

    // Sends data to Python
    $.getJSON("/records", {
        'numberOfProblems': numberOfProblems,
        'correct': correctAns,
        'time': min * 60 + sec + milisec / 1000
    }, function(data, textStatus, jqXHR) {
        giveMark(data, correctAns, numberOfProblems, min, sec, milisec);
    });

}

// Checks if there is no the same pair of numbers in the arrays
function checkPreviousDiv(mas_a, mas_b, temp_a, temp_b) {
    for (var k = 0; k < mas_a.length; k++) {
        if (temp_a == mas_a[k] && temp_b == mas_b[k]) {
            return true;
        }
    }
    return false;
}

// Checks if there is no the same pair of numbers in the arrays
function checkPreviousAddMul(mas_a, mas_b, temp_a, temp_b) {
    for (var k = 0; k < mas_a.length; k++) {
        if (temp_a == mas_a[k] && temp_b == mas_b[k] || temp_a == mas_b[k] && temp_b == mas_a[k]) {
            return true;
        }
    }
    return false;
}

// Gives the place, number of correct answers, number of problems, mark and time
function giveMark(place, j, numberOfProb, min_t, sec_t, milisec_t) {

    // Calculates the mark
    if (j == numberOfProb) {
        var mark = 'Perfect';
    } else if (j >= .9 * numberOfProb && j < numberOfProb) {
        mark = 'Excelent';
    } else if (j >= .82 * numberOfProb && j < .9 * numberOfProb) {
        mark = 'Very good';
    } else if (j >= .74 * numberOfProb && j < .82 * numberOfProb) {
        mark = 'Good';
    } else if (j >= .64 * numberOfProb && j < .74 * numberOfProb) {
        mark = 'Bad';
    } else if (j >= .6 * numberOfProb && j < .64 * numberOfProb) {
        mark = 'Very bad';
    } else {
        mark = 'Poor';
    }

    // Shows the message with: place, correct answers, number of problems, mark, time
    return alert('Your place is ' + place + '.\nNumber of correct answers ' + j + ' from ' + numberOfProb +
        ' questions.\nYour mark is ' + mark + '.\nYou spent ' + min_t + ' minutes ' + sec_t + ' seconds ' +
        milisec_t + ' miliseconds.');
}

// Gives random integer from min to max including
function randomInteger(min, max) {
    var rand = min + Math.random() * (max + 1 - min);
    return Math.floor(rand);
}