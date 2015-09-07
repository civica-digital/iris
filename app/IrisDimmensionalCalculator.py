from threading import Thread
from oauth2client.client import SignedJwtAssertionCredentials
#import configparser
import os
import gspread
import yaml
import hashlib

import i18n

i18n.load_path.append('app/locales/')
i18n.set('locale', 'es')
i18n.set('fallback', 'en')
_ = i18n.t

raw_ref = open("app/static/content/descripcion-indicadores.yml").read()
ref = yaml.load(raw_ref)['Descripción de los indicadores']

class IrisDimmensionalCalculator(Thread):

	def __init__(self, url,queue):
		Thread.__init__(self)
		self.url = url
		self.queue = queue

	def run(self):
		docid = self.get_docid(self.url)
		keyset = self.get_keyset()
		auth = self.authenticate(keyset['email'], keyset['password'])
		raw_data = self.read_data(auth, docid)
		data = self.extract_data(raw_data)
		readiness_scores = self.assess_readiness(data)
		self.queue.put(readiness_scores)


	def get_docid(self, url):
		tokens = url.split('/')
		docid = ""
		for token in tokens:
			if len(token)==44: docid = token
		return docid

	def get_keyset(self):
		#config = configparser.ConfigParser()
		#config.read(['./irisdc', os.path.expanduser('~/.irisdc')])

		keyset = {}
		keyset['email'] = os.environ.get('EMAIL_USER')
		keyset['password'] = os.environ.get('PASSWORD_USER')
		#keyset['email'] = config.get("keyset",'email')
		#keyset['password'] = config.get("keyset",'password')

		return keyset

	def authenticate(self, email, password):
		# OAuth2 implementation, used "password" to refer to API key value of credentials.

		scope = ['https://spreadsheets.google.com/feeds']
		#Must replace passwords "\\n" by "\n", as its a product of python misreading the environmental variable password
		credentials = SignedJwtAssertionCredentials(email, bytes(password.replace("\\n","\n"),'utf-8'), scope)
		auth = gspread.authorize(credentials)
		return auth

	def hash_questions(self,questions_list):
		hashed_questions_list = []
		for question in questions_list:
			hashed_questions_list.append(hashlib.sha256(question.encode()).hexdigest())
		print(questions_list)
		return hashed_questions_list

	def read_data(self, auth, docid):
		# Opens a worksheet from spreadsheet from its key
		sh = auth.open_by_key(docid)
		worksheet = sh.sheet1
		# Gets all values from the first row and hash them.
		question_list = self.hash_questions(worksheet.row_values(0))
		answers_list = worksheet.row_values(2)
		return dict(zip(question_list,answers_list))

	# Extracts the data and loads it to a dictionary
	def extract_data(self, raw_data):
		# Note: These variables must be loaded form elsewhere, preferrably the stylesheet.
		variable_names_per_question = {'0036d88bdf0ab49ac66e44a8341ce9258db95f1114c502bf2cc8c3b64313626c': 'leg_license_comments', '00418921e6a3ff90aaece7b0bc406bde38479ec112fa4dac81dbc8b1f58966dc': 'funds_inprocess', '1728783ab07ec4897a6f65af21cf1c20c55cebfb6d100de8d59c7d01fabef1ec': 'funds_percentage', '19ac4c453edd20904ed3a0083300c2fd835295766980d44530a78c1f06ee6762': 'cap_quality', '1e2fb5ad07338c37ba9cd703ff62a1964d3f556bca71a0c88fe7cf3f51b2fcaf': 'cap_od_time', '271656efff6f716dea9336d1fb1508890dbacdcebef09193781fd5191cccbc45': 'soc_events', '286c8e8bd3fa1969512400f4f3040ef74c8bf1d81b57962b62dacebc72314c14': 'opn_spreadsheets', '2a117e48ac85b533a36932ab8bea01ad22cdeb9c9db7ce224f8815fe3452f6e6': 'funds_sources', '2e0a93919c4114b68095270817d2db9258c14f179f68c60b0d0d9db63d703735': 'cap_management', '2f5e3a59144eccd93d6e8607aa6cbbae68341bce78aaa55af7a6dcfa163de97e': 'cap_teamsize', '3ea29847f0f8e8e8ad3167a85e593d302e243b917389f86d37b6e3998601877a': 'opn_plaintext', '3fbb511b82561c95337ba39b3836020a64e45a7869150e8acbfe87cd18270662': 'imp_self_assessment', '4b08f8773d4cc2277b2e112b6f7aa054c1011f05fab4109434860ceeb94c3a6c': 'cap_od_tools', '592823ad0b7e0432138f46f3ee7569bbc2392a2b1885aff567c8ba905f56e5b0': 'leg_decree', '5d6f549dee61dc2ba4664b581c2145b43061a49b7d79d96a132ad0462b093c08': 'cap_frequency', '6192982a5d29442dee55d374b66fc076ad348d47a69f39b5ed4892753d56d768': 'cap_content_tools', '708412bd049b512b62093afd1211aa63373fadfb5cb35a6ce6e8912629603554': 'lead_official', '719c9e2ed1b53b641f92d3aa449e37eabc22304bdf679faae8c03c2a8e1a53ee': 'opn_physical', '733363efe4639ec5c2ff63cfa87760fb8e8b01b8d7d404972e92e7c9af50a68a': 'cap_dbms', '7dfade61796f5950add6e5f01aeb7f9b8dee814dfe38e57b5ef3d2c4e2a12778': 'cap_design', '85ace3c1b5cecf48c032c6f0db2251814cf59570a0c1a8c37adf5253c950743d': 'opn_training_agencies', '8be58f477f4c5b6e4f17510ece84f50e5d5bcd12039181064114297d58e93928': 'leg_state_status', '90c570d66b2976fe5cb6b300855e92228fd4aebe5c480fd0267c3b793cf38023': 'soc_allies', '98385021c8ea05f0427bc00aeabc74ab40832ef51cdd24453feb39e291fdf3f6': 'opn_training', '9b4eabbedcf705071546c1f02c45420cf7c5bb2139115246b12bab9e089c464b': 'opn_training_technical', '9d9504829d2f516e41643dcfa36d3e277003b59f4d8a9e211d326fac8eabd31f': 'cap_content_time', '9da3cedb8d4023f2d61a5aabb00ff7644f4c0daf7b2f47d5bad4c339ebdea461': 'leg_license', 'a0bdf23cb87f759300db8060bba371c0ea55192c1ba7fe12b69c44ba5394fd59': 'leg_state_reference', 'a3c7e89accd6cd97d5df892363a7d7f18cd0e14eddc0527e4f56dfbb0717f8f3': 'cap_extteam', 'a5b50681379deb9df81153c30a63f6fade9423f731ce0a490b6aca4bfd49ac88': 'opn_training_org', 'bf765818d5f07681c19db434b377cd99b3fb15caabf4daa8ab9fe56a1afd4dc7': 'funds_exercised', 'c3b792293b283089c2a1a660018c4ba55bb1c32ab02386abf4cbe69d79595066': 'opn_scans', 'd2fa3c1fc26bda9b52181a6d7cdbcad48656a23d67a5309d72201a3375dc2d0e': 'timestamp', 'da907904c86aa7ccdf727ca3d7e1813fbf0ab5ed78e85d5bdb6512db00e2980f': 'opn_training_legal', 'df7c92cb31f5afd5e525ebc6f2cf03a84f6fc8197249995cf2fe40e852a18d52': 'funds_budget', 'e518155c36597a388e8c1337e492fe2c893862cd1974482f5b492454af8310b2': 'cap_content_budget', 'f2df9c4687f63d9bc692cc8e644d5b6dc8165c518589cbf891a22d2f21512280': 'opn_geospatial', 'f562767d4a69a92aabc3d26611b75c18f20a9d86f203b79c884aca5a6ce9031e': 'cap_metadata', 'f58ec01ae208c392aeee70c5814da4daa8357007fbfc49abab309fa5159d4773': 'lead_unofficial'}
		answers_dict = {}
		for key, variable in raw_data.items():
			variable_question = variable_names_per_question[key]
			answers_dict[variable_question] = raw_data[key]
		return answers_dict

	def set_max_grade(self, data):
		max_grade = 1.0
		rounded = float(data)
		if data >= max_grade: rounded = 0.99
		return rounded

	def percentage_to_decimal(self, inputdata):
		data = inputdata.strip("%")
		data = float(data)
		data_percentage = data/100.0
		return data_percentage

	def assess_readiness(self, data):
		leadership_score = self.get_leadership_score(data)
		fundings_score = self.get_fundings_score(data)
		capabilities_score = self.get_capabilities_score(data)
		openness_score = self.get_openness_score(data)
		legal_score = self.get_legal_score(data)
		society_score = self.get_society_score(data)
		impact_score = self.get_impact_score(data)

		readiness_scores = []
		leaderdic = {'axis': _('iris.leadership'),
					 'value': leadership_score,
					 'desc': ref['leadership']}
		readiness_scores.append(leaderdic)

		fundic = {'axis': _('iris.fundings'),
				  'value': fundings_score,
				  'desc': ref['fundings']}
		readiness_scores.append(fundic)

		capdic = {'axis': _('iris.capabilities'),
				  'value': capabilities_score,
				  'desc': ref['capabilities']}
		readiness_scores.append(capdic)

		opdic = {'axis': _('iris.openness'),
				 'value': openness_score,
				 'desc': ref['openness']}
		readiness_scores.append(opdic)

		legdic = {'axis': _('iris.legal'),
		          'value': legal_score,
				  'desc': ref['legal']}
		readiness_scores.append(legdic)

		socdic = {'axis': _('iris.society'),
		          'value': society_score,
				  'desc': ref['society']}
		readiness_scores.append(socdic)

		impdic = {'axis': _('iris.impact'),
		          'value': impact_score,
				  'desc': ref['impact']}
		readiness_scores.append(impdic)


		return readiness_scores

	# Leadership score
	def get_leadership_score(self, data):
		# Calculates the score for official allies.
		official_score = 0
		# Calculates the score for unofficial allies.
		unofficial_score = 0

		official_allies = data['lead_official'].split(', ')
		unofficial_allies = data['lead_unofficial'].split(', ')

		# Note: This should be customizable and loaded from elsewhere.
		allies_weight = {
			'Alcalde': 5,
			'Regidores de Oposición': 3,
			'Secretario de Ayuntamiento': 3,
			'Grupos de Empresarios o Sindicatos': 3,
			'Síndicos': 2,
			'Regidores': 2,
			'IFAI': 2,
			'Persona a cargo de las políticas de datos abiertos en la ciudad': 2,
			'Organizaciones de la sociedad civil': 1,
			'Ciudadanos Individuales': 1,
		}
		multiplier = 3  # Determines the factor by which an official ally will be multiplied.
		for ally in official_allies:
			if ally in allies_weight.keys():
				ally_score = allies_weight[ally]*multiplier
				official_score += ally_score

		for ally in unofficial_allies:
			if ally in allies_weight.keys():
				unofficial_score += allies_weight[ally]

		leadership_score = (official_score + unofficial_score)/30

		leadership_score = self.set_max_grade(leadership_score)

		leadership_todo = 1.0  - leadership_score

		return leadership_todo

	# Fundings score
	def get_fundings_score(self, data):

		inprocess_sum = 0

		# To do: Validate presence, input is s a number, valid characters, ranges[0,100]
		budget_data = data['funds_percentage']
		budget = budget_data.strip("%")
		budget = float(budget)
		budget_percentage = budget/100.0

		# Note: Need to be extracareful here when handling the 'Otra' field.
		sources_inprocess = data['funds_inprocess'].split(', ')

		for source in sources_inprocess:
			inprocess_sum += 1

		fundings_score = budget_percentage * (1+(0.05 * inprocess_sum))
		fundings_score = self.set_max_grade(fundings_score)

		fundings_todo = 1.0 - fundings_score

		return fundings_todo

	# Institutional Structures and Skills score
	def get_capabilities_score(self, data):

		capabilities_sum = 0

		# To do: Validate fields
		team_size = float(data['cap_teamsize']) # Technical team size.
		team_time = float(data['cap_od_time']) # Total time, in hours, devoted weekly to technical duties.

		if team_size >= 1 and team_time >= 40:
			capabilities_sum += 2

		# Open Data management tools
		# To do: Validate fields
		data_tools = data['cap_od_tools'].split(', ')
		for tool in data_tools:
			if tool == 'No instalado todavía':
				capabilities_sum += 0
			else:
				capabilities_sum += 3

		# Metadata
		metadata = data['cap_metadata']
		# Validate for keywords such as 'Ninguna', 'Ninguno', 'No sé', 'N/A', 'N/D', etc.
		if metadata:
			capabilities_sum += 1

		update_frequency = data['cap_frequency']
		if update_frequency == 'Mensual' or update_frequency == 'Semanal' or update_frequency == 'Inemdiatas':
			capabilities_sum += 2
		elif update_frequency == 'Semestral' or update_frequency == 'Varía':
			capabilities_sum += 1
		elif update_frequency == 'No se actualizan':
			capabilities_sum += 0
		else:
			capabilities_sum += 1

		# Content management tools
		content_tools = data['cap_content_tools']
		if content_tools == 'Ninguno':
			capabilities_sum += 0
		else:
			capabilities_sum += 1

		# Database management system
		cap_dbms = data['cap_dbms']
		if cap_dbms == 'Ninguno':
			capabilities_sum += 0
		else:
			capabilities_sum += 1

		capabilities_score = capabilities_sum/12

		capabilities_score = self.set_max_grade(capabilities_score)

		capabilities_todo = 1.0 - capabilities_score
		return capabilities_todo

	# Degree of Dataset Openness score
	def get_openness_score(self, data):
		openness_sum = 0

		scanned = float(data['opn_scans']) # Validate
		if scanned > 0:
			openness_sum += 1

		spreadsheets = float(data['opn_spreadsheets']) # Validate
		if spreadsheets > 0:
			openness_sum += 2

		plaintext = float(data['opn_plaintext']) # Validate
		if plaintext > 0:
			openness_sum += 3

		geospatial = float(data['opn_geospatial']) # Validate
		if geospatial > 0:
			openness_sum += 3


		opn_training = float(data['opn_training'])

		if opn_training == 1:
			openness_sum += 1

		#1 point if one training, 2 points if more than one trainings
		#1 point more if more than one agency with a course given.

		opn_training_technical = data['opn_training_technical']
		opn_training_technical = self.percentage_to_decimal(opn_training_technical)

		opn_training_org = data['opn_training_org']
		opn_training_org = self.percentage_to_decimal(opn_training_org)

		opn_training_legal = data['opn_training_legal']
		opn_training_legal = self.percentage_to_decimal(opn_training_legal)

		if opn_training_org > 0 or opn_training > 0:
			openness_sum += 2

		opn_training_agencies = float(data['opn_training_agencies']) #Validate

		if opn_training_agencies > 1:
			openness_sum += 1

		openness_score = openness_sum/8

		openness_score = self.set_max_grade(openness_score)

		openness_todo = 1.0 - openness_score

		return openness_todo

	# Policy/Legal Framework score
	def get_legal_score(self, data):
		legal_sum = 0

		local_law_status = data['leg_local_status']
		if local_law_status == 'Establecida':
			legal_sum += 2
		elif local_law_status == 'En planeación':
			legal_sum += 1

		state_law_status = data['leg_state_status']
		if state_law_status == 'Establecida':
			legal_sum += 2
		elif state_law_status == 'En planeación':
			legal_sum += 1

		#license = data['leg_license']
		#leg_license_comments = data['leg_license_comments']
		#leg_decree = data['leg_decree']
		#leg_local_reference = data['leg_local_reference']
		#leg_state_reference = data['leg_state_reference']

		legal_score = legal_sum/4.0

		legal_score = self.set_max_grade(legal_score)

		legal_todo = 1.0 - legal_score

		return legal_todo

	# Society Readiness score
	def get_society_score(self, data):
		society_sum = 0

		# Validate this
		allies = data['soc_allies'].split(", ")
		if len(allies) > 1:
			society_sum += 2
		elif len(allies) == 1:
			society_sum += 1

		planned_events = data['soc_events']
		if planned_events == 'Si':
			society_sum += 1

		society_score = society_sum/3

		society_score = self.set_max_grade(society_score)

		society_todo = 1.0 - society_score

		return society_todo

	# Impact Evaluation score
	def get_impact_score(self, data):
		impact_sum = 0
		# Validate this
		assessment_mechanisms = data['imp_self_assessment'].split(", ")
		for element in assessment_mechanisms:
			impact_sum += 1

		impact_score = impact_sum/2.0

		impact_score = self.set_max_grade(impact_score)

		impact_todo = 1.0 - impact_score

		return impact_todo

# Argument Parser for offline review
#def get_args():
#	parser = argparse.ArgumentParser()
#	parser.add_argument('--url')
#	return parser.parse_args()
