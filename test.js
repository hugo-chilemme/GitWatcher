const axios = require('axios');

const query = `
  query($usernames: [String!]!) {
    users: rateLimit {
      cost
      remaining
      resetAt
    }
    search(query: "type:user", type: USER, first: 50) {
      nodes {
        ... on User {
          login
          commits: contributionsCollection(contributionTypes: [COMMIT], first: 100) {
            totalCount
            nodes {
              commit {
                message
              }
            }
          }
          pullRequests: contributionsCollection(contributionTypes: [PULL_REQUEST], first: 100) {
            totalCount
            nodes {
              pullRequest {
                title
              }
            }
          }
        }
      }
    }
  }
`;

const getUsersCommitsAndPullRequests = async (usernames) => {
  const variables = {
    usernames: usernames,
  };

  const headers = {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${process.env.GITHUB_ACCESS_TOKEN}`,
  };

  const response = await axios.post('https://api.github.com/graphql', { query, variables }, { headers });

  if (response.data.errors) {
    throw new Error(response.data.errors.map((error) => error.message).join(', '));
  }

  const users = response.data.search.nodes;

  const results = {};

  for (let user of users) {
    const username = user.login;
    const commits = user.commits.nodes.map((node) => node.commit.message);
    const pullRequests = user.pullRequests.nodes.map((node) => node.pullRequest.title);

    results[username] = {
      commits: commits,
      pullRequests: pullRequests,
    };
  }

  return results;
};

const usernames = ['HugoCLI', 'RedginaldGodeau'];

getUsersCommitsAndPullRequests(usernames)
  .then((results) => console.log(results))
  .catch((error) => console.error(error));
