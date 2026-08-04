export default function LatestPublications({
  publications,
}) {

  return (

    <div className="container py-5">

      <h2 className="mb-4">
        📄 Latest Publications
      </h2>

      <div className="list-group">

        {publications.map((publication) => (

          <div
            key={publication.id}
            className="list-group-item"
          >

            <strong>
              {publication.title}
            </strong>

            <br />

            <small>
              {publication.publication_year}
            </small>

          </div>

        ))}

      </div>

    </div>

  );

}
