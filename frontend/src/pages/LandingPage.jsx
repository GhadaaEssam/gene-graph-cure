import { Link } from "react-router-dom";

function LandingPage() {
  return (
    <div className="container text-center mt-5">
      <h1>GeneGraphCure</h1>
      <p>Predicting Cancer Drug Resistance</p>
      <Link to="/predict" className="btn btn-primary">
        Go to Prediction
      </Link>
    </div>
  );
}

export default LandingPage;