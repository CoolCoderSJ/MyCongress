import cohere, os, json
import requests
from flask import Flask, request
from flask_cors import CORS
import psycopg2

conn = psycopg2.connect(
        host="localhost",
        database="shuchir_congressional24",
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASS'])

app = Flask(__name__)
CORS(app)
co = cohere.Client(api_key=os.environ['COHERE_API_KEY'])

@app.route('/api/summarize', methods=['POST'])
def summarize():
    bills = request.json['bills']
    print(bills)

    summaries = []
    texts = []
    ids = []

    for bill in bills:
        if bill['url'] == "No text available":
            ids.append(bill['billNumber'])
            continue
        try:
            billId = bill['url'].split("/")[5]
            ids.append(billId)
            bill = requests.get(bill['url']).text.split("<pre>")[1].split("</pre>")[0]
            cur = conn.cursor()
            cur.execute("SELECT summary FROM summaries WHERE billNumber = %s", (billId,))
            result = cur.fetchone()
            if result:
                summary = result[0]
                summaries.append({"billNumber": billId, "summary": summary})
                continue
            cur.close()
            texts.append(f"billNumber: {billId}\n" + bill)
        except:
            summaries.append(bill)

    t2 = texts

    incomplete = []

    for i in range(0, len(texts), 4):
        t = "\nNEW BILL\n".join(texts[i:i+4])

        while True:
            response = co.chat(
            message='summarize each of the following U.S. bills in a few understandable sentences. No need to include information about sponsors/co-sponsors. Each response should use only one bill. Generate the output as JSON. Add each summary to an object with the billNumber and the summary. The bill number is provided, preceeding the actual bill contents. It is prefixed with "billNumber: ". Use this number in the object, and no other identifier. Add each object to an array called summaries. Each bill below will be separated by the words "NEW BILL"\n' + t,
            model="command-r-plus-08-2024",
            response_format={
                "type": "json_object",
                "schema": {
                    "type": "object",
                    "properties": {
                        "summaries": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "billNumber": {"type": "string"},
                                    "summary": {"type": "string"}
                                },
                                "required": ["billNumber", "summary"]
                            }
                        }
                    },
                    "required": ["summaries"]
                }
            }
            )

            if response.text == "":
                t = t.split("\nNEW BILL\n")
                incomplete.append(t[-1])
                t.remove(t[-1])
                t = "\nNEW BILL\n".join(t)
                continue

            print(response, file=open("response.txt", "a"))
            summaries += json.loads(response.text)['summaries']
            break

    for i in incomplete:
        billNumber = i.split("\n")[0].split("billNumber: ")[1]
        response = co.chat(
        message='summarize the following U.S. bill in a few understandable sentences. No need to include information about sponsors/co-sponsors. Generate the output as JSON. Add each summary to an object with the billNumber and the summary. The bill number is provided, preceeding the actual bill contents. It is prefixed with "billNumber: ". Use this number in the object, and no other identifier. Add the object to an array called summaries. \n' + i,
        model="command-r-plus-08-2024",
        response_format={
            "type": "json_object",
            "schema": {
                "type": "object",
                "properties": {
                    "summaries": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "billNumber": {"type": "string"},
                                "summary": {"type": "string"}
                            },
                            "required": ["billNumber", "summary"]
                        }
                    }
                },
                "required": ["summaries"]
            }
        }
        )

        if response.text == "":
            continue

        print(response, file=open("response.txt", "a"))
        s = json.loads(response.text)['summaries']
        s[0]['billNumber'] = billNumber
        summaries += s

    for bId in ids:
        try:
            summary = next(item for item in summaries if item["billNumber"] == bId)
        except:
            summary = {"billNumber": bId, "summary": "An error occurred while summarizing this bill or the text was not available. Please try again later."}
            summaries.append(summary)

    s2 = summaries
    for s in summaries:
        if s['billNumber'] not in ids:
            s2.remove(s)
    summaries = s2

    print(summaries)
    cur = conn.cursor()
    for summary in summaries:
        if summary['summary'] == "An error occurred while summarizing this bill or the text was not available. Please try again later.":
            continue
        cur.execute(
            "INSERT INTO summaries (billNumber, summary) VALUES (%s, %s) ON CONFLICT (billNumber) DO UPDATE SET summary = EXCLUDED.summary",
            (summary['billNumber'], summary['summary'])
        )
    conn.commit()
    cur.close()

    return summaries

app.run('0.0.0.0', 9145, debug=True)