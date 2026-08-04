export default function UpcomingConferences({
  conferences,
}) {

  return (

    <div className="container py-5">

      <h2 className="mb-4">
        📅 Upcoming Conferences
      </h2>

      <div className="row">

        {conferences.map((conference) => (

          <div
            key={conference.id}
            className="col-md-4 mb-3"
          >

            <div className="card shadow border-0">

              <div className="card-body">

                <h5>
                  {conference.title}
                </h5>

              </div>

            </div>

          </div>

        ))}

      </div>

    </div>

  );

}
