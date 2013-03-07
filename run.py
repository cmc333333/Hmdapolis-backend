from flask import abort, Flask, Response, request
import json
import psycopg2

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

cities = {
    31084: 'Los Angeles',  16974: 'Chicago',      19124: 'Dallas', 
    35644: 'NYC',          44060: 'Spokane',      12580: 'Baltimore',
    12420: 'Austin',       35380: 'New Orleans',  24340: 'Grand Rapids',
    41884: 'San Francisco',14484: 'Boston',       42644: 'Seattle',
    12060: 'Atlanta',      26900: 'Indianapolis', 33460: 'St. Paul',
    19780: 'Des Moines',   39300: 'Providence',   40900: 'Sacramento',
    45220: 'Tallahassee',  22020: 'Fargo',        41180: 'St. Louis',
    29620: 'Lansing',      34980: 'Nashville',    39580: 'Raleigh',
    38900: 'Portland',     30460: 'Lexington',    43620: 'Sioux Falls',
    39900: 'Reno',         29820: 'Las Vegas',    17900: 'Columbia',
    47894: 'D.C',          13820: 'Birmingham',   26420: 'Houston',
    11260: 'Anchorage',    26180: 'Honolulu',     19740: 'Denver'
    }


def jsonp(to_return):
    if request.args.get("callback"):
        return request.args.get("callback") + \
                '(' + json.dumps(to_return) + ')'
    return json.dumps(to_return)

@app.route("/agency/")
def agencies_handler():
    return jsonp([{'id': agency[0], 'name': agency[1]} for agency 
        in agencies if agency])

@app.route("/city/")
def cities_handler():
    return jsonp(cities)

@app.route("/apply/")
def apply():
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
        agency = request.args.get('agency')
        if agency not in [a[0] for a in agencies if a]:
            abort(400)
        agency = (idx for idx,a in enumerate(agencies) 
                if a and a[0] == agency).next()
        if agency == 4 or agency == 9:  #   OTS -> CFPB
            agency_pair = (4,9)
        else:
            agency_pair = (agency,)
        income = int(request.args.get('applicant_income'))
    except ValueError:
        abort(400)

    if year < 6 or year > 11:
        abort(400)

    query = """
        SELECT count(*), action_type 
        FROM hmda 
        WHERE year = %s 
        AND msa_md = %s 
        AND action_type IN (1,2,3,7,8) 
        AND agency IN %s 
        AND loan_amount > %s AND loan_amount < %s 
        AND applicant_income > %s AND applicant_income < %s 
        GROUP BY action_type;
        """
    cursor.execute(query, (year + 2000, msa_md, agency_pair,
        loan_amount-15, loan_amount+15, income-10, income+10))

    results = {'accepted': 0, 'rejected': 0}
    for row in cursor.fetchall():
        results[actions[row[1]][1]] += row[0]

    return jsonp(results)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8180, debug=True)
