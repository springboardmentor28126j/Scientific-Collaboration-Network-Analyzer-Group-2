function CustomCard({ children }) {

    return (

        <div
            className="card border-0 shadow rounded-4 h-100 custom-card"
        >

            <div className="card-body">

                {children}

            </div>

        </div>

    );

}

export default CustomCard;