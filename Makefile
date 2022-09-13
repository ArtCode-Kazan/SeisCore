VERSION="1.0.1"


create-image:
	docker build -t seiscore:$(VERSION) .
	docker build -t ghcr.io/mikkoartik/seiscore:$(VERSION) .

upload-image:
	docker push ghcr.io/mikkoartik/seiscore:$(VERSION)


load-image:
	docker pull ghcr.io/mikkoartik/seiscore:$(VERSION)
