import { Card } from "react-bootstrap";
import "../styles/pagecard.css";

function PageCard({ title, children }) {

    return (

        <Card className="page-card">

            <Card.Body>

                <h3 className="page-title">

                    {title}

                </h3>

                {children}

            </Card.Body>

        </Card>

    );

}

export default PageCard;