import api from "../api/api";

export const search = async ({
  q,
  type = "all",
  page = 1,
  pageSize = 10,
  year = "",
  publicationType = "",
  status = "",
  institution = "",
  sort = "relevance",
}) => {
  const response = await api.get("/search", {
    params: {
      q,
      type,
      page,
      page_size: pageSize,
      year: year || undefined,
      publication_type: publicationType || undefined,
      status: status || undefined,
      institution: institution || undefined,
      sort,
    },
  });

  return response.data;
};
