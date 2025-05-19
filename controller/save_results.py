import json

#def save_to_json(data, filename="results.json"):
    #with open(filename, "w", encoding="utf-8") as f:
        #json.dump(data, f, indent=4, ensure_ascii=False)


def save_to_json(data, output_dir):
    import json
    with open(f"{output_dir}/summary.json", "w",encoding="utf-8") as f:
        json.dump(data, f, indent=2,ensure_ascii=False)
