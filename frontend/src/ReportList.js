import React, { useEffect, useState } from 'react';
import axios from 'axios';
import Table from 'react-bootstrap/Table';
import Container from 'react-bootstrap/Container';

const ReportList = ({ userEmail }) => {
  const [reports, setReports] = useState([]);

  useEffect(() => {
    axios.get(`http://127.0.0.1:8000/geoprocess/reports/${userEmail}/`)
      .then(response => {
        setReports(response.data.user_reports);
      })
      .catch(error => {
        console.error('Error fetching reports:', error);
      });
  }, [userEmail]);

  return (
    <div>
      <Container>
        <Table striped bordered hover>
          <thead>
            <tr>
              <th>ID</th>
              <th>Título</th>
              <th>Descripción</th>
              <th>Status</th>
              <th>Archivo</th>
            </tr>
          </thead>
          <tbody>
            {reports.map(report => (
              <tr key={report.id}>
                <td>{report.id}</td>
                <td>{report.title}</td>
                <td>{report.description}</td>
                <td>{report.status}</td>
                <td>
                  <a href={report.file} target="_blank" rel="noopener noreferrer">
                    Descargar
                  </a>
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      </Container>
    </div>
  );
};

export default ReportList;
