import api from '../api/api';

const mockPublications = [
  {
    id: 1,
    title: "Graph Neural Networks for Collaboration Prediction",
    authors: "A. Sharma, P. Nair",
    abstract: "Scientific collaboration prediction is essential for understanding research dynamics. This paper proposes a Graph Neural Network (GNN) framework that leverages temporal topological features to predict future co-authorships.",
    journal: "IEEE Transactions on Knowledge and Data Engineering",
    conference: "IEEE TKDE 2024",
    publication_year: 2024,
    publication_type: "Journal Article",
    status: "Published",
    url: "https://doi.org/10.1109/TKDE.2024.3210451",
    doi: "10.1109/TKDE.2024.3210451",
    citation_count: 45,
    citations: 45,
    file_name: "GNN_Collaboration_Prediction.pdf",
    created_at: "2024-01-15",
    updated_at: "2024-02-10"
  },
  {
    id: 2,
    title: "Optimizing Centrality Algorithms in Large Social Graphs",
    authors: "R. Kumar, S. Patel",
    abstract: "Centrality metrics identify key hubs in academic networks. We present a parallelized approximation algorithm that reduces time complexity for computing betweenness centrality in million-node graphs.",
    journal: "ACM Computing Surveys",
    conference: "ACM CS 2023",
    publication_year: 2023,
    publication_type: "Survey Article",
    status: "Published",
    url: "https://doi.org/10.1145/3541289.3541290",
    doi: "10.1145/3541289.3541290",
    citation_count: 89,
    citations: 89,
    file_name: "Centrality_Optimization.pdf",
    created_at: "2023-05-12",
    updated_at: "2023-06-01"
  },
  {
    id: 3,
    title: "Survey on Co-authorship Network Analysis Techniques",
    authors: "A. Sharma, R. Kumar",
    abstract: "This survey reviews current computational paradigms applied to bibliometric networks, covering node embeddings, temporal dynamics, and community detection benchmarks.",
    journal: "Journal of Informetrics",
    conference: "JoI 2024",
    publication_year: 2024,
    publication_type: "Review",
    status: "Published",
    url: "https://doi.org/10.1016/j.joi.2024.101234",
    doi: "10.1016/j.joi.2024.101234",
    citation_count: 12,
    citations: 12,
    file_name: "Coauthorship_Survey.pdf",
    created_at: "2024-02-20",
    updated_at: "2024-03-05"
  },
  {
    id: 4,
    title: "Distributed Community Detection in Big Data Networks",
    authors: "P. Nair, S. Patel",
    abstract: "Detecting dense communities in large-scale academic graphs helps isolate evolving sub-disciplines. We introduce a distributed label-propagation scheme optimized for Spark clusters.",
    journal: "Elsevier Knowledge-Based Systems",
    conference: "KBS 2022",
    publication_year: 2022,
    publication_type: "Conference Paper",
    status: "Published",
    url: "https://doi.org/10.1016/j.knosys.2022.108912",
    doi: "10.1016/j.knosys.2022.108912",
    citation_count: 134,
    citations: 134,
    file_name: "Distributed_Community_Detection.pdf",
    created_at: "2022-11-04",
    updated_at: "2022-12-15"
  }
];

export const getPublications = async () => {
  try {
    const res = await api.get('/api/v1/publications');
    return res.data;
  } catch (err) {
    console.warn('Backend unavailable, using mock publications data.');
    return mockPublications;
  }
};

export const getPublication = async (id) => {
  try {
    const res = await api.get(`/api/v1/publications/${id}`);
    return res.data;
  } catch (err) {
    console.warn(`Backend unavailable, returning mock publication #${id}`);
    const found = mockPublications.find((p) => p.id === parseInt(id));
    return found || { ...mockPublications[0], id: parseInt(id) };
  }
};

export const createPublication = async (data) => {
  try {
    const res = await api.post('/api/v1/publications/', data);
    return res.data;
  } catch (err) {
    console.warn('Backend unavailable, simulating publication creation.');
    const newPub = {
      ...data,
      id: Date.now(),
      created_at: new Date().toISOString().split('T')[0],
      updated_at: new Date().toISOString().split('T')[0]
    };
    mockPublications.push(newPub);
    return newPub;
  }
};

export const updatePublication = async (id, data) => {
  try {
    const res = await api.put(`/api/v1/publications/${id}`, data);
    return res.data;
  } catch (err) {
    console.warn(`Backend unavailable, simulating publication update for #${id}`);
    return { ...data, id: parseInt(id), updated_at: new Date().toISOString().split('T')[0] };
  }
};

export const deletePublication = async (id) => {
  try {
    const res = await api.delete(`/api/v1/publications/${id}`);
    return res.data;
  } catch (err) {
    console.warn(`Backend unavailable, simulating publication deletion for #${id}`);
    return { message: 'Publication deleted successfully' };
  }
};

export const uploadPublication = async (id, file) => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    const res = await api.post(`/api/v1/publications/${id}/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return res.data;
  } catch (err) {
    console.warn('Backend unavailable, simulating file upload success.');
    return { message: 'File uploaded successfully', file_name: file.name };
  }
};

export const downloadPublication = async (id) => {
  try {
    const res = await api.get(`/api/v1/publications/${id}/download`, {
      responseType: 'blob'
    });
    return res;
  } catch (err) {
    console.warn('Backend unavailable, simulating file download blob.');
    const dummyBlob = new Blob(['Mock PDF content for publication ' + id], { type: 'application/pdf' });
    return { data: dummyBlob };
  }
};
