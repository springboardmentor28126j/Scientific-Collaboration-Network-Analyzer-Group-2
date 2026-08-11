import api from '../api/api';

const mockConferences = [
  { id: 1, acronym: "KDD 2024", name: "ACM SIGKDD Conference on Knowledge Discovery and Data Mining", location: "Barcelona, Spain", year: 2024, impactScore: "9.8/10", website: "https://kdd.org/kdd2024" },
  { id: 2, acronym: "NeurIPS 2024", name: "Conference on Neural Information Processing Systems", location: "Vancouver, Canada", year: 2024, impactScore: "9.9/10", website: "https://neurips.cc" },
  { id: 3, acronym: "ICSE 2024", name: "International Conference on Software Engineering", location: "Lisbon, Portugal", year: 2024, impactScore: "9.2/10", website: "https://icse2024.org" }
];

export const getConferences = async () => {
  try {
    const res = await api.get('/api/v1/conferences');
    return res.data;
  } catch (err) {
    return mockConferences;
  }
};

export const getConference = async (id) => {
  try {
    const res = await api.get(`/api/v1/conferences/${id}`);
    return res.data;
  } catch (err) {
    return mockConferences.find(c => c.id === parseInt(id)) || mockConferences[0];
  }
};

export const createConference = async (data) => {
  try {
    const res = await api.post('/api/v1/conferences/', data);
    return res.data;
  } catch (err) {
    return { ...data, id: Date.now() };
  }
};

export const updateConference = async (id, data) => {
  try {
    const res = await api.put(`/api/v1/conferences/${id}`, data);
    return res.data;
  } catch (err) {
    return { ...data, id: parseInt(id) };
  }
};
