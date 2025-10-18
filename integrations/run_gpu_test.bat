@echo off
echo Starting GPU Test...
echo ================ > gpu_output.txt
echo GPU-Enabled Model Evaluation Test >> gpu_output.txt
echo =============================== >> gpu_output.txt

python run_gpu_tests_fixed.py >> gpu_output.txt 2>&1

echo Test completed. Check gpu_output.txt for results.
type gpu_output.txt
