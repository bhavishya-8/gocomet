from flask import Flask, jsonify 
import json

app = Flask("__name__")

def worker_stats():
    stats_dir = '/path/to/your/stats/directory'  # Update this with the actual directory path
    # Load the existing data from final_stats.json (if it exists)
    final_stats = {}
    final_stats_file = f'{stats_dir}/final_stats.json'
    
    try:
        with open(final_stats_file, 'r') as existing_file:
            final_stats = json.load(existing_file)
    except FileNotFoundError:
        # Handle the case where the file doesn't exist yet
        pass
    
    # Assuming worker_stats is a dictionary with updated data
    # Update the corresponding sections in final_stats
    final_stats['section1'] = worker_stats.get('section1', {})
    final_stats['section2'] = worker_stats.get('section2', {})
    final_stats['section3'] = worker_stats.get('section3', {})
    final_stats['section4'] = worker_stats.get('section4', {})
    
    # Write the updated final_stats data to final_stats.json
    with open(final_stats_file, 'w') as final_file:
        json.dump(final_stats, final_file, indent=4)
    
    # Return the updated worker_stats data as a JSON response
    return jsonify(worker_stats)

if "__main__" == "__name__":
    app.run(host='0.0.0.0', port="3000", debug=True)
