import api from '../api/api';

const mockResearchers = [
  { id: 1, name: "Dr. Aravind Sharma", title: "Senior Professor & Network Researcher", institution: "IIT Bombay", domain: "Artificial Intelligence", email: "aravind.sharma@iitb.ac.in", papers: 42, citations: 1250, hIndex: 18, i10Index: 24, bio: "Specializes in Graph Neural Networks, Social Network Analysis, and Complex Network Mining." },
  { id: 2, name: "Prof. Sunita Nair", title: "Associate Professor & Data Mining Expert", institution: "IISc Bengaluru", domain: "Network Analysis", email: "sunita.nair@iisc.ac.in", papers: 38, citations: 980, hIndex: 15, i10Index: 19, bio: "Focuses on large-scale network algorithms, dynamic graph representations, and cross-institutional collaboration modeling." },
  { id: 3, name: "Dr. Rajesh Kumar", title: "Assistant Professor", institution: "BITS Pilani", domain: "Graph Mining", email: "rajesh.kumar@pilani.bits-pilani.ac.in", papers: 29, citations: 610, hIndex: 12, i10Index: 15, bio: "Conducts research in graph mining, topological link prediction algorithms, and citation network structures." },
  { id: 4, name: "Dr. Sneha Patel", title: "Lead AI Researcher", institution: "IIT Delhi", domain: "Machine Learning", email: "sneha.patel@iitd.ac.in", papers: 51, citations: 1890, hIndex: 22, i10Index: 28, bio: "Specializes in scalable machine learning models for complex biological and academic collaboration networks." }
];

export const getResearchers = async () => {
  try {
    const res = await api.get('/researchers/');
    return res.data;
  } catch (err) {
    return mockResearchers;
  }
};

export const getResearcher = async (id) => {
  try {
    const res = await api.get(`/researchers/${id}`);
    return res.data;
  } catch (err) {
    return mockResearchers.find(r => r.id === parseInt(id)) || mockResearchers[0];
  }
};

export const createResearcher = async (data) => {
  try {
    const res = await api.post('/researchers/', data);
    return res.data;
  } catch (err) {
    return { ...data, id: Date.now() };
  }
};

export const updateResearcher = async (id, data) => {
  try {
    const res = await api.put(`/researchers/${id}`, data);
    return res.data;
  } catch (err) {
    return { ...data, id: parseInt(id) };
  }
};
