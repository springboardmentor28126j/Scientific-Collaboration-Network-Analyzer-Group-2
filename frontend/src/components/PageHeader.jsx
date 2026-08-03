function PageHeader({

    title,
    icon,
    buttonText,
    buttonIcon,
    onClick

}) {

    return (

        <div className="d-flex justify-content-between align-items-center mb-4">

            <div>

                <h2 className="fw-bold">

                    <i className={`bi ${icon} text-primary me-2`}></i>

                    {title}

                </h2>

            </div>

            {

                buttonText &&

                <button
                    className="btn btn-primary rounded-pill px-4"
                    onClick={onClick}
                >

                    <i className={`bi ${buttonIcon} me-2`}></i>

                    {buttonText}

                </button>

            }

        </div>

    );

}

export default PageHeader;