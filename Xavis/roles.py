from rolespermissions.roles import AbstractUserRole

class Doctor (AsctractUserRole):
	available_permissions={
		'create_medical_record':True
	}

class Nurse(AbstractUserRole):
		available_permissions={
			'edit_patient_file':True
		}