export default async function sendCommand(command: string, args: string[]) {
  return fetch("http://newsframe:5000/command", {
    method: "POST",
    mode: 'cors',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      command, arguments: args.join(' ')
    })
  }).then(async res => {
    const data = await res.text()
    return data
  })

}