export default function TopInstitutions({
  institutions,
}) {

  return (

    <div className="container py-5">

      <h2 className="mb-4">
        🏛 Top Institutions
      </h2>

      <div className="row">

        {institutions.map((institution) => (

          <div
            key={institution.id}
            className="col-md-4 mb-3"
          >

            <div className="card shadow border-0">

              <div className="card-body">

                <h5>
                  {institution.name}
                </h5>

              </div>

            </div>

          </div>

        ))}

      </div>

    </div>

  );

}
