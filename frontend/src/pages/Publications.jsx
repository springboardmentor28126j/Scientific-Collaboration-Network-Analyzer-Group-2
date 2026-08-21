import { useEffect, useState } from "react";
import axios from "axios";
import "../css/Publications.css";

function Publications() {
  const [publications, setPublications] = useState([]);
  const [showForm, setShowForm] = useState(false);

  const [formData, setFormData] = useState({
    title: "",
    abstract: "",
    keywords: "",
    author: "",
    journal: "",
    year: "",
    status: "Draft",
    pdf_file: "",
    researcher_id: ""
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get(
          "http://127.0.0.1:8001/publications/"
        );

        setPublications(response.data);
      } catch (error) {
        console.log(error);
      }
    };

    fetchData();
  }, []);

  const loadPublications = async () => {
    try {
      const response = await axios.get(
        "http://127.0.0.1:8001/publications/"
      );

      setPublications(response.data);
    } catch (error) {
      console.log(error);
    }
  };

  const handleChange = (event) => {
    setFormData({
      ...formData,
      [event.target.name]: event.target.value
    });
  };

  const addPublication = async (event) => {
    event.preventDefault();

    try {
      await axios.post(
        "http://127.0.0.1:8001/publications/",
        {
          title: formData.title,
          abstract: formData.abstract || null,
          keywords: formData.keywords || null,
          author: formData.author,
          journal: formData.journal,
          year: Number(formData.year),
          status: formData.status,
          pdf_file: formData.pdf_file || null,
          researcher_id: Number(formData.researcher_id)
        }
      );

      alert("Publication added successfully!");

      setFormData({
        title: "",
        abstract: "",
        keywords: "",
        author: "",
        journal: "",
        year: "",
        status: "Draft",
        pdf_file: "",
        researcher_id: ""
      });

      setShowForm(false);

      loadPublications();
    } catch (error) {
      console.log(error);
      alert("Failed to add publication");
    }
  };

  const deletePublication = async (id) => {
    if (
      !window.confirm(
        "Are you sure you want to delete this publication?"
      )
    ) {
      return;
    }

    try {
      await axios.delete(
        `http://127.0.0.1:8001/publications/${id}`
      );

      alert("Publication deleted successfully!");

      loadPublications();
    } catch (error) {
      console.log(error);
      alert("Failed to delete publication");
    }
  };

  return (
    <div className="container">

      <h2>Publications</h2>

      <button onClick={() => setShowForm(!showForm)}>
        {showForm ? "Close Form" : "Add Publication"}
      </button>

      {showForm && (
        <form onSubmit={addPublication}>

          <input
            type="text"
            name="title"
            placeholder="Title"
            value={formData.title}
            onChange={handleChange}
            required
          />

          <input
            type="text"
            name="abstract"
            placeholder="Abstract"
            value={formData.abstract}
            onChange={handleChange}
          />

          <input
            type="text"
            name="keywords"
            placeholder="Keywords"
            value={formData.keywords}
            onChange={handleChange}
          />

          <input
            type="text"
            name="author"
            placeholder="Author"
            value={formData.author}
            onChange={handleChange}
            required
          />

          <input
            type="text"
            name="journal"
            placeholder="Journal"
            value={formData.journal}
            onChange={handleChange}
            required
          />

          <input
            type="number"
            name="year"
            placeholder="Year"
            value={formData.year}
            onChange={handleChange}
            required
          />

          <select
            name="status"
            value={formData.status}
            onChange={handleChange}
          >
            <option value="Draft">Draft</option>
            <option value="Published">Published</option>
            <option value="Submitted">Submitted</option>
          </select>

          <input
            type="text"
            name="pdf_file"
            placeholder="PDF File"
            value={formData.pdf_file}
            onChange={handleChange}
          />

          <input
            type="number"
            name="researcher_id"
            placeholder="Researcher ID"
            value={formData.researcher_id}
            onChange={handleChange}
            required
          />

          <button type="submit">
            Save Publication
          </button>

        </form>
      )}

      <div className="table-wrapper">

        <table>

          <thead>
            <tr>
              <th>ID</th>
              <th>Title</th>
              <th>Abstract</th>
              <th>Keywords</th>
              <th>Author</th>
              <th>Journal</th>
              <th>Year</th>
              <th>Status</th>
              <th>PDF File</th>
              <th>Researcher ID</th>
              <th>Action</th>
            </tr>
          </thead>

          <tbody>

            {publications.map((pub) => (

              <tr key={pub.publication_id}>

                <td>
                  {pub.publication_id}
                </td>

                <td>
                  {pub.title}
                </td>

                <td>
                  {pub.abstract || "-"}
                </td>

                <td>
                  {pub.keywords || "-"}
                </td>

                <td>
                  {pub.author}
                </td>

                <td>
                  {pub.journal}
                </td>

                <td>
                  {pub.year}
                </td>

                <td>
                  {pub.status}
                </td>

                <td>
                  {pub.pdf_file || "-"}
                </td>

                <td>
                  {pub.researcher_id || "-"}
                </td>

                <td>
                  <button
                    onClick={() =>
                      deletePublication(
                        pub.publication_id
                      )
                    }
                  >
                    Delete
                  </button>
                </td>

              </tr>

            ))}

          </tbody>

        </table>

      </div>

    </div>
  );
}

export default Publications;