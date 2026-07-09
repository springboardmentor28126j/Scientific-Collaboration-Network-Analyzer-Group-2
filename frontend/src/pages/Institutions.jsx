import { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";
import Footer from "../components/Footer";
import api from "../services/api";

import "../styles/institutions.css";

function Institutions() {

  const [institutions, setInstitutions] = useState([]);

  useEffect(() => {
    api.get("/institutions/")
      .then((res) => {
        setInstitutions(res.data);
      })
      .catch((err) => {
        console.log(err);
      });
  }, []);

  return (
    <>
      <Navbar />

      <div className="dashboard-container">

        <Sidebar />

        <div className="institutions-content">

          <h2>🏫 Institutions</h2>

          <table className="institutions-table">

            <thead>

              <tr>
                <th>ID</th>
                <th>Institution</th>
                <th>Country</th>
                <th>City</th>
                <th>Website</th>
                <th>Established</th>
              </tr>

            </thead>

            <tbody>

              {institutions.map((item) => (

                <tr key={item.id}>

                  <td>{item.id}</td>
                  <td>{item.institution_name}</td>
                  <td>{item.country}</td>
                  <td>{item.city}</td>
                  <td>
                    <a href={item.website} target="_blank" rel="noreferrer">
                      Visit
                    </a>
                  </td>
                  <td>{item.established_year}</td>

                </tr>

              ))}

            </tbody>

          </table>

        </div>

      </div>

      <Footer />

    </>
  );
}

export default Institutions;