from flask import abort, Flask, Response, request
import json

app = Flask(__name__)

actions = [
    None, 
    ('Loan originated', 'accepted'),
    ('Application approved but not accepted', 'accepted'),
    ('Application denied by financial institution', 'rejected'),
    ('Application withdrawn by applicant', 'other'),
    ('File closed for incompleteness', 'other'),
    ('Loan purchased by the institution', 'other'),
    ('Preapproval request denied by financial institution', 'rejected'),
    ('Preapproval request approved but not accepted', 'accepted')
    ]
agencies = [
    None,
    ('OCC','Office of the Comptroller of the Currency'),
    ('FRS','Federal Reserve System'),
    ('FDIC','Federal Deposit Insurance Corporation'),
    ('OTS', 'Office of Thrift Supervision'),
    ('NCUA', 'National Credit Union Administration'),
    None,
    ('HUD', 'Department of Housing and Urban Development'),
    None,
    ('CFPB', 'Consumer Financial Protection Bureau')
    ]


@app.route("/")
def hello():
    data = {'response': [
        {'name': 'accepted', 'count': 8},
        {'name': 'rejected', 'count': 4},
        ]}
    if request.args.get("callback"):
        callback = request.args.get("callback")
        return callback + '(' + json.dumps(data) + ');'
    return json.dumps(data)

@app.route("/dev/")
def dev():
    import psycopg2
    conn = psycopg2.connect("dbname=hmda user=hmda password=hmda")
    cursor = conn.cursor()

    if not request.args.get('year')\
        or not request.args.get('loan_amount')\
        or not request.args.get('msa_md')\
        or not request.args.get('agency')\
        or not request.args.get('applicant_income'):
        abort(400)
    
    try:
        year = int(request.args.get('year'))
        loan_amount = int(request.args.get('loan_amount'))
        msa_md = int(request.args.get('msa_md'))
        agency = int(request.args.get('agency'))
        if agency == 4 or agency == 9:  #   OTS -> CFPB
            agency_pair = (4,9)
        else:
            agency_pair = (agency,)
        income = int(request.args.get('applicant_income'))
    except ValueError:
        abort(400)

    if year < 6 or year > 11:
        abort(400)

    year = "hmda%02d" % (year,)

    query = """
        SELECT count(*), action_type 
        FROM """ + year + """
        WHERE loan_amount > %s AND loan_amount < %s AND msa_md=%s 
        AND applicant_income > %s AND applicant_income < %s
        AND action_type IN (1,2,3,7,8) AND agency IN %s
        GROUP BY action_type; 
        """
    cursor.execute(query, (loan_amount-15, loan_amount+15, msa_md, 
        income-10, income+10, agency_pair))

    results = {'accepted': 0, 'rejected': 0}
    for row in cursor.fetchall():
        results[actions[row[1]][1]] += row[0]

    if request.args.get("callback"):
        return request.args.get("callback") + \
            '(' + json.dumps(results) + ');'

    return json.dumps(results)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8180, debug=True)
