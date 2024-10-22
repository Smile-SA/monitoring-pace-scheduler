#!/bin/bash

# Total duration in minutes
total_duration=60
# Duration for each test run (in seconds)
test_duration=$((3 * 60 + 30)) # 3 minutes and 30 seconds
# Pause duration between tests (in seconds)
pause_duration=90

# Function to run the Gatling test
run_test() {
    echo "Starting Gatling test with a timeout of $test_duration seconds..."
    timeout $test_duration ./mvnw gatling:test -Dgatling.simulationClass=computerdatabase.ComputerDatabaseSimulation
    if [ $? -eq 124 ]; then
        echo "Gatling test timed out after $test_duration seconds."
    else
        echo "Gatling test completed."
    fi
}

# Run the test in a loop for the total duration
end_time=$((SECONDS + total_duration * 60))
while [ $SECONDS -lt $end_time ]; do
    run_test
    echo "Pausing for $pause_duration seconds..."
    sleep $pause_duration
done

echo "Test cycle completed."
