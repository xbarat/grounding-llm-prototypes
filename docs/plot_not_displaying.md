# Plot Not Displaying in Frontend

## Issue
The visualization was being generated in the backend but not displaying in the frontend. Instead, plots were either:
- Opening in a desktop window, or
- Being saved locally without appearing in the UI

## Root Cause
The issue stemmed from the order of operations in the plot generation process:

1. `plt.show()` was being called in the generated code before we could capture the figure data
2. When `plt.show()` is called, it displays the plot and clears the current figure
3. Our subsequent attempt to capture the figure data was happening after the figure was cleared

## Solution
We implemented a two-part fix:

1. Modified `execute_code_safely` in `backend/app/analyst/generate.py` to:
   ```python
   # Capture code inserted before any plt.show() calls
   capture_code = """
   # Get the current figure
   fig = plt.gcf()
   # Save to buffer
   buffer = io.BytesIO()
   fig.savefig(buffer, format='png', bbox_inches='tight')
   buffer.seek(0)
   captured_figure = base64.b64encode(buffer.getvalue()).decode()
   """
   
   # Insert capture code before plt.show()
   if "plt.show()" in modified_code:
       modified_code = modified_code.replace("plt.show()", capture_code + "\nplt.show()")
   else:
       modified_code = modified_code + "\n" + capture_code
   ```

2. Updated the prompt in `backend/app/analyst/prompts.py` to explicitly instruct the model:
   ```
   Important guidelines:
   ...
   7. DO NOT use plt.show() - the figure will be handled programmatically
   8. DO NOT use plt.savefig() - the figure will be handled externally
   ```

## Testing
The fix was verified using a unit test that:
1. Creates a test plot
2. Ensures the figure is captured before any `plt.show()` calls
3. Verifies the base64 image data is properly generated

## Key Learnings
1. Matplotlib's `show()` function clears the current figure
2. When generating plots programmatically, always capture the figure data before any display operations
3. Base64 encoding allows for efficient transfer of plot data from backend to frontend 