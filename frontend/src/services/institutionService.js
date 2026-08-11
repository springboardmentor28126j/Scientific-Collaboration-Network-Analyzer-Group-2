import api from '../api/api';

const mockInstitutions = [
  { id: 1, name: "Indian Institute of Technology Bombay", abbreviation: "IITB", city: "Mumbai", state: "Maharashtra", country: "India", email: "contact@iitb.ac.in", phone: "+91-22-25722545", website: "www.iitb.ac.in", address: "Powai, Mumbai", authorsCount: 142, totalPubs: 820 },
  { id: 2, name: "Indian Institute of Science", abbreviation: "IISc", city: "Bengaluru", state: "Karnataka", country: "India", email: "contact@iisc.ac.in", phone: "+91-80-22932001", website: "www.iisc.ac.in", address: "CV Raman Road, Bengaluru", authorsCount: 195, totalPubs: 1140 },
  { id: 3, name: "BITS Pilani", abbreviation: "BITS", city: "Pilani", state: "Rajasthan", country: "India", email: "admissions@pilani.bits-pilani.ac.in", phone: "+91-1596-245073", website: "www.bits-pilani.ac.in", address: "Vidya Vihar, Pilani", authorsCount: 88, totalPubs: 410 },
  { id: 4, name: "IIT Delhi", abbreviation: "IITD", city: "New Delhi", state: "Delhi", country: "India", email: "webmaster@admin.iitd.ac.in", phone: "+91-11-26591000", website: "www.iitd.ac.in", address: "Hauz Khas, New Delhi", authorsCount: 130, totalPubs: 750 }
];

export const getInstitutions = async () => {
  try {
    const res = await api.get('/institutions/');
    return res.data;
  } catch (err) {
    return mockInstitutions;
  }
};

export const getInstitution = async (id) => {
  try {
    const res = await api.get(`/institutions/${id}`);
    return res.data;
  } catch (err) {
    return mockInstitutions.find(i => i.id === parseInt(id)) || mockInstitutions[0];
  }
};

export const createInstitution = async (data) => {
  try {
    const res = await api.post('/institutions/', data);
    return res.data;
  } catch (err) {
    return { ...data, id: Date.now() };
  }
};

export const updateInstitution = async (id, data) => {
  try {
    const res = await api.put(`/institutions/${id}`, data);
    return res.data;
  } catch (err) {
    return { ...data, id: parseInt(id) };
  }
};
