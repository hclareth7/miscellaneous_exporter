#!python
import socket
import os

controllers = os.environ.get('CONTROLLERS').split(',')

print("metrics:")


def check_tcp():
    for x in controllers:
        sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock_tcp.settimeout(5)  # Setting timeout 5sec
        result_tcp = sock_tcp.connect_ex((x, 53))
        if result_tcp == 0:
            print(f"""- metric: "designate_tcp_port"
  description: "designate_tcp_port_check"
  type: "gauge"
  value: 1
  labels:
  - label: "status"
    value: "opened"
  - label: "designate_controller_ip"
    value: {x}""")
        else:
            print(f"""- metric: "designate_tcp_port"
  description: "designate_tcp_port_check"
  type: "gauge"
  value: 0
  labels:
  - label: "status"
    value: "closed"
  - label: "designate_controller_ip"
    value: {x}""")
    sock_tcp.close()


def check_udp():
    for y in controllers:
        sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock_tcp.settimeout(5)  # Setting timeout 5sec
        result_tcp = sock_tcp.connect_ex((y, 53))
        if result_tcp == 0:
            print(f"""- metric: "designate_upd_port"
  description: "designate_udp_port_check"
  type: "gauge"
  value: 1
  labels:
  - label: "status"
    value: "opened"
  - label: "designate_controller_ip"
    value: {y}
              """)
        else:
            print(f"""- metric: "designate_upd_port"
  description: "designate_upd_port_check"
  type: "gauge"
  value: 0
  labels:
  - label: "status"
    value: "closed"
  - label: "designate_controller_ip"
    value: {y}""")
    sock_tcp.close()


if __name__ == "__main__":
    check_tcp()
    check_udp()
