from flask import escape 
import functions_framework
import json
from flask import Flask, request, jsonify, Response

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


cred = credentials.Certificate("election-api-49e66-firebase-adminsdk-tq88w-7c8375b8dc.json")
firebase_admin.initialize_app(cred)
db = firestore.client()


app = Flask(__name__)

# voters = db.collections("voters")
# elections = db.collections("elections")
# results = db.collections("results")

@functions_framework.http
def hello_http(request):
    request_body = request.get_json(silent=True)
    if request.method == 'POST' and 'voter_ID' in request_body:
        return create_voter(request)

    elif request.method == 'GET' and request.path == '/':
        return index()
    
    elif request.method == 'DELETE' and 'voter_ID' in request_body:
        return delete_user()
    
    elif request.method == 'PUT' and 'voter_ID' in request_body:
        return edit_voter()
    
    elif request.method == 'GET'  and request.path == '/voters':
        if 'voter_ID' in request_body:
            return get_voter(request)
        else:
            return get_all_voters(request)
        
    elif request.method == 'POST'  and request.path == '/elections':
        return create_election()
    
    elif request.method == 'DELETE'  and request.path == '/elections':
        return delete_election()
    
    elif request.method == 'GET'  and request.path == '/elections':
        if 'election_ID' in request_body:
            return get_elections()
        else:
            return get_all_elections()
        
    elif request.method == 'PATCH'  and request.path == '/vote':
        return cast_vote()
    
    elif request.method == 'GET'  and request.path == '/results':
        return get_results()
    
    


@app.route('/', methods=['GET'])
def index():
    return "Ashesi Election Site"


@app.route('/voters', methods=['POST'])
def create_voter(request):
    data = request.get_json()
    new_voter = json.loads(request.data)
    voters_ref = db.collection('voters')

    existing_voters = [doc.to_dict() for doc in voters_ref.get()]

    for voter in existing_voters:
        if voter['voter_ID'] == new_voter['voter_ID']:
            return jsonify({'error': 'User with this ID already exists'}), 409

    voters_ref = db.collection('voters').document(new_voter['voter_ID'])
    voters_ref.set(new_voter)
    # return "Entered create function"


    return jsonify(new_voter), 201


    

@app.route('/voters', methods=['DELETE'])
def delete_user():
    voters_ref = db.collection('voters')

    to_delete = json.loads(request.data)

    voter_query = voters_ref.where('voter_ID', '==', to_delete['voter_ID'])
    voter_docs = voter_query.get()
    print(voter_docs)

    if not voter_docs:
        return jsonify({'error': 'User with this ID does not exist'}), 404

    for doc in voter_docs:
        doc.reference.delete()

    return jsonify(to_delete)


@app.route('/voters', methods=['PUT'])
def edit_voter():
        to_edit = json.loads(request.data)

        voters_ref = db.collection('voters')


        voter_query = voters_ref.where('voter_ID', '==', to_edit['voter_ID'])
        voter_docs = voter_query.get()

        if len(voter_docs) == 0:
            return jsonify({'error': 'User with this ID does not exist'}), 404

        for doc in voter_docs:
            doc.reference.update({
                'major': to_edit['major'],
                'year_group': to_edit['year_group']
            })

        return jsonify(to_edit), 200

# @functions_framework.http
@app.route('/voters', methods=['GET'])
def get_all_voters(request):
    voters_ref = db.collection('voters')

    voter_docs = voters_ref.get()

    all_voters = []

    for doc in voter_docs:
        all_voters.append(doc.to_dict())

    if len(all_voters) == 0:
        return jsonify({'error': 'Voter directory empty'}), 404

    return jsonify(all_voters)
   

@app.route('/voters', methods=['GET'])
def get_voter(request):
    voters_ref = db.collection('voters')
    to_edit = json.loads(request.data)

    voter_query = voters_ref.where('voter_ID', '==', to_edit['voter_ID'])
    voter_docs = voter_query.get()

    if len(voter_docs) == 0:
            return jsonify({'error': 'User with this ID does not exist'}), 404
    for voter in voter_docs:
        voter_dict = voter.to_dict()
        return jsonify(voter_dict)









           
       

# #         #################    ELECTION     #########################
# @functions_framework.http
@app.route('/elections', methods=['POST'])
def create_election():
    new_election = json.loads(request.data)
    elections_ref = db.collection('Elections')

    existing_election_query = elections_ref.where('election_ID', '==', new_election['election_ID'])
    existing_election_docs = existing_election_query.get()

    if len(existing_election_docs) > 0:
        return jsonify({'error': 'Election with this ID already exists'}), 409

    elections_ref.add(new_election)

    return jsonify(new_election)

        

# # #Delete election v1 creates a new list and then append everythin else into that list except the record that contains the requested voter ID
# # #Return 404 when the requested item to be deleted does not exist?
# # #Boolean variable that is changed to true if the requested value is found and if loop executes fully and boolean is still True 
# # @functions_framework.http
@app.route('/elections', methods=['DELETE'])
def delete_election():
    to_delete = json.loads(request.data)
    elections_ref = db.collection('Elections')

    existing_election_query = elections_ref.where('election_ID', '==', to_delete['election_ID'])
    existing_election_docs = existing_election_query.get()

    if len(existing_election_docs) == 0:
        return jsonify({'error': 'Election with this ID does not exist'}), 404

    for doc in existing_election_docs:
        doc.reference.delete()

    return jsonify(to_delete)

# # # ISSUE - Get all voters with this method, get particular voter with
# # #similar method that may have id in URI and should be election[S]
# # @functions_framework.http
@app.route('/elections', methods=['GET'])
def get_elections():
    to_get = json.loads(request.data)
    req_election_id = to_get['election_ID']
    elections_ref = db.collection('Elections')

    existing_election_query = elections_ref.where('election_ID', '==', req_election_id)
    existing_election_docs = existing_election_query.get()

    if len(existing_election_docs) == 0:
        return jsonify({'error': 'Election with this ID does not exist'}), 404

    election_data = existing_election_docs[0].to_dict()
    return jsonify(election_data)
   
# # @functions_framework.http
@app.route('/elections', methods=['GET'])
def get_all_elections():
    all_elections = []
    elections_ref = db.collection('Elections')
    existing_election_docs = elections_ref.get()

    for election_doc in existing_election_docs:
        election_data = election_doc.to_dict()
        all_elections.append(election_data)

    if not all_elections:
        return jsonify({'error': 'Election Database empty'}), 404

    return jsonify(all_elections)


# # #To vote, a voter's ID and the ID of the candidate to be voted for will be needed
# # #Using PATCH is for updating just some of the fields in the resource and since it does not send the complete resource representation it is more bandwidth efficient 
# # @functions_framework.http
@app.route('/vote', methods=['PATCH'])
def cast_vote():
    vote_data = json.loads(request.data)
    voter_id = vote_data['voter_ID']
    election_id = vote_data['election_ID']
    candidate_id = vote_data['candidate_ID']

    # Retrieve the selected election document from Firebase
    election_ref = db.collection('Elections').document(election_id)
    selected_election = election_ref.get().to_dict()

    # Validate the selected election and candidate
    if not selected_election:
        return jsonify({'error': 'Invalid election ID'}), 404

    curr_votes = selected_election.get('votes', [])
    candidate_found = False

    for vote in curr_votes:
        if vote['candidate_id'] == candidate_id:
            # Check if user ID is not already in votes
            if voter_id not in vote['voter_IDs']:
                vote['voter_IDs'].append(voter_id)
                candidate_found = True
                break

    if not candidate_found:
        return jsonify({'error': 'Invalid candidate ID'}), 404

    # Update the selected election document in Firebase
    election_ref.update({'votes': curr_votes})

    return jsonify(curr_votes)



# # #Results URI will return the results of the events as they currently stand 
# # # ISSUE - Could also returns a boolean indicating whether the election is over or not.
# # # Assumption here is that a call to results is made when the election is over, otherwise the returned data would not be written to a file unless a check is done to find out whether the election is over
# # # if not, there would be a need to call results again and thus there will be multiple results for the same election in the election file causing possible discrepancies
# # @functions_framework.http
 
@app.route('/results', methods=['GET'])
def get_results():
    elections_ref = db.collection('Elections')
    election_id = request.args.get('election_ID')
    print(election_id)

    # Query the "Elections" collection for the requested election
    election_doc = elections_ref.document(election_id).get()
    if not election_doc.exists:
        return jsonify({'error': 'Election not found'})

    election_data = election_doc.to_dict()

    election_results = {}
    election_results['name'] = election_data['name']
    election_results['candidate_results'] = []

    # Access each candidate in the given election, find the name from the candidates list and their corresponding number of votes from the votes list
    for candidate in election_data['candidates']:
        candidate_votes = {}
        candidate_name = candidate['candidate_name']
        candidate_id = candidate['candidate_id']
        for result in election_data['votes']:
            if result['candidate_id'] == candidate_id:
                number_votes = len(result['voter_IDs'])
                candidate_votes['candidate_name'] = candidate_name
                candidate_votes['no_votes'] = number_votes
                election_results['candidate_results'].append(candidate_votes)

    # Write the results to the "Results" collection
    results_ref = db.collection('Results').document(election_id)
    results_ref.set(election_results)

    return jsonify(election_results)
    

# app.run(debug=True)
